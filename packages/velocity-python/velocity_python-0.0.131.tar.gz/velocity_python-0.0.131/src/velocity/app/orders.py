import datetime
import support.app
import pprint
import velocity.db

engine = velocity.db.postgres.initialize()
REQUIRED = object()


@engine.transaction
class Order:
    SCHEMA = {
        "headers": {
            "customer_email": REQUIRED,
            "order_date": REQUIRED,
            "order_type": REQUIRED,
        },
        "lineitems": {
            "sku": REQUIRED,
            "qty": REQUIRED,
            "price": REQUIRED,
        },
        "lineitems_supp": {
            "note": str,
        },
    }

    DEFAULTS = {
        "headers": {
            "order_date": lambda: datetime.date.today(),
            "effective_date": lambda: datetime.date.today(),
        }
    }

    def __init__(self, order_id=None):
        self.order_id = order_id
        self.headers = {}
        self.lineitems = {}
        self.lineitems_supp = {}

    def __repr__(self):
        return f"Order(order_id={self.order_id}, headers={pprint.pformat(self.headers)}, lineitems={pprint.pformat(self.lineitems)}, lineitems_supp={pprint.pformat(self.lineitems_supp)})"

    def exists(self, tx):
        if not self.order_id:
            raise ValueError("order_id must be set to check existence")
        return tx.table("orders").find(self.order_id)

    def __bool__(self):
        return bool(self.order_id) and self.exists(engine.transaction())

    def load(self, tx):
        if not self.order_id:
            raise ValueError("order_id must be set to load an order")

        order = tx.table("orders").one(self.order_id)
        if not order:
            raise ValueError(f"Order {self.order_id} not found")

        self.headers = dict(order)

        items = (
            tx.table("order_lineitems")
            .select(where={"order_id": self.order_id}, orderby="line_number")
            .all()
        )
        for idx, row in enumerate(items):
            self.lineitems[idx] = dict(row)

        supps = (
            tx.table("order_lineitems_supp")
            .select(where={"order_id": self.order_id}, orderby="line_number")
            .all()
        )
        for idx, row in enumerate(supps):
            self.lineitems_supp[idx] = dict(row)

    def update_header(self, key, value):
        self.headers[key] = value

    def add_lineitem(self, data: dict, supp_data: dict = None):
        index = len(self.lineitems)
        self.lineitems[index] = data
        self.lineitems_supp[index] = supp_data or {}

    def update_lineitem(self, index: int, data: dict = None, supp_data: dict = None):
        if index not in self.lineitems:
            raise IndexError(f"No line item at index {index}")
        if data:
            self.lineitems[index].update(data)
        if supp_data is not None:
            self.lineitems_supp[index].update(supp_data)

    def delete_lineitem(self, index: int):
        if index not in self.lineitems:
            raise IndexError(f"No line item at index {index}")
        del self.lineitems[index]
        if index in self.lineitems_supp:
            del self.lineitems_supp[index]
        self._reindex_lineitems()

    def _reindex_lineitems(self):
        """Re-index lineitems and supplemental data after deletion."""
        new_items = {}
        new_supps = {}
        for i, key in enumerate(sorted(self.lineitems)):
            new_items[i] = self.lineitems[key]
            new_supps[i] = self.lineitems_supp.get(key, {})
        self.lineitems = new_items
        self.lineitems_supp = new_supps

    def _apply_defaults(self):
        for section, defaults in self.DEFAULTS.items():
            target = getattr(self, section)
            for key, default in defaults.items():
                if key not in target:
                    target[key] = default() if callable(default) else default
                elif key == "updated_at":
                    # Always update updated_at if present
                    target[key] = default() if callable(default) else default

    def _validate(self):
        self._apply_defaults()

        for key, requirement in self.SCHEMA["headers"].items():
            if requirement is REQUIRED and key not in self.headers:
                raise ValueError(f"Missing required header field: {key}")
            if (
                key in self.headers
                and requirement is not REQUIRED
                and not isinstance(self.headers[key], requirement)
            ):
                raise TypeError(
                    f"Header field '{key}' must be of type {requirement.__name__}"
                )

        for idx, item in self.lineitems.items():
            for key, requirement in self.SCHEMA["lineitems"].items():
                if requirement is REQUIRED and key not in item:
                    raise ValueError(f"Line item {idx} missing required field: {key}")

        for idx, supp in self.lineitems_supp.items():
            for key, expected in self.SCHEMA["lineitems_supp"].items():
                if key in supp and not isinstance(supp[key], expected):
                    raise TypeError(
                        f"Supplemental field '{key}' in item {idx} must be of type {expected.__name__}"
                    )

    def persist(self, tx):
        self._validate()

        if self.order_id:
            tx.table("orders").update(self.headers, self.order_id)
        else:
            record = tx.table("orders").new(self.headers)
            self.order_id = record["sys_id"]

        tx.table("order_lineitems").delete(where={"order_id": self.order_id})
        tx.table("order_lineitems_supp").delete(where={"order_id": self.order_id})

        for index in sorted(self.lineitems):
            tx.table("order_lineitems").insert(
                {
                    "order_id": self.order_id,
                    "line_number": index,
                    **self.lineitems[index],
                }
            )
            tx.table("order_lineitems_supp").insert(
                {
                    "order_id": self.order_id,
                    "line_number": index,
                    **self.lineitems_supp.get(index, {}),
                }
            )

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "headers": self.headers,
            "lineitems": self.lineitems,
            "lineitems_supp": self.lineitems_supp,
        }
