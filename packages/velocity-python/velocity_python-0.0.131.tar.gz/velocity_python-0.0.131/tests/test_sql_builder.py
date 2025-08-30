import unittest
from velocity.db.servers import postgres
from velocity.db.core.table import Query
import sqlparse

test_db = "test_foreign_key_db"
engine = postgres.initialize(database=test_db)


@engine.transaction
class TestSqlBuilder(unittest.TestCase):

    def test_basic_select(self, tx):
        sql, vals = tx.table("child_table").select(
            columns=[
                "parent_id>name",
                "middle_id>title",
                "sys_id",
                "description",
            ],
            where={
                "sys_id": 1,
                "parent_id>name": None,
                "in_list": [1, 2, 3, 4, 5],
                "in_tuple": (1, 2, 3, 4, 5),
                "!something": Query("Select * from table where sys_id = %s", (1000,)),
                "!=notequal": 2,
                "><between": [1, 10],
            },
            groupby="parent_id>name, middle_id>title",
            having={"<>parent_id>name": "test"},
            orderby="parent_id>name desc, middle_id>title asc, sys_id desc",
            sql_only=True,
        )

        expected_sql = """SELECT B.name,
       C.title,
       A.sys_id,
       A.description
FROM child_table AS A
LEFT JOIN parent_table AS B ON A.parent_id = parent_table.sys_id
LEFT JOIN middle_table AS C ON A.middle_id = middle_table.sys_id
WHERE A.sys_id = %s
  AND B.name IS NULL
  AND A.in_list IN %s
  AND A.in_tuple IN %s
  AND A.something NOT IN
    (SELECT *
     FROM TABLE
     WHERE sys_id = %s)
  AND A.notequal <> %s
  AND A.between BETWEEN %s AND %s
GROUP BY B.name,
         C.title
HAVING B.name <> %s
ORDER BY B.name DESC,
         C.title ASC,
         sys_id DESC"""
        self.assertEqual(sql, expected_sql)
        self.assertEqual(
            vals, (1, [1, 2, 3, 4, 5], [1, 2, 3, 4, 5], 1000, 2, 1, 10, "test")
        )

    def test_select_with_wildcard(self, tx):
        sql, vals = tx.table("users").select(sql_only=True)
        expected_sql = "SELECT * FROM users"
        expected_sql = sqlparse.format(
            expected_sql, reindent=True, keyword_case="upper"
        )
        self.assertEqual(sql, expected_sql)
        self.assertEqual(vals, ())

    def test_select_with_columns(self, tx):
        sql, vals = tx.table("users").select(columns=["id", "name"], sql_only=True)
        expected_sql = "SELECT id, name FROM users"
        expected_sql = sqlparse.format(
            expected_sql, reindent=True, keyword_case="upper"
        )
        self.assertEqual(sql, expected_sql)
        self.assertEqual(vals, ())

    def test_select_with_distinct(self, tx):
        sql, vals = tx.table("users").select(columns="DISTINCT id, name", sql_only=True)
        print(sql)
        expected_sql = "SELECT DISTINCT id, name FROM users"
        expected_sql = sqlparse.format(
            expected_sql, reindent=True, keyword_case="upper"
        )
        self.assertEqual(sql, expected_sql)
        self.assertEqual(vals, ())

    def test_select_with_join(self, tx):
        sql, vals = tx.table("users").select(
            columns=["id", "name", "profile>email"],
            where={"profile>email": "test@example.com"},
            sql_only=True,
        )
        print(sql)
        expected_sql = (
            'SELECT "A"."id", "A"."name", "B"."email" AS "profile_email" '
            'FROM "users" AS "A" '
            'LEFT OUTER JOIN "profile" AS "B" '
            'ON "A"."profile_id" = "B"."id" '
            'WHERE "B"."email" = %s'
        )
        self.assertEqual(sql, expected_sql)
        self.assertEqual(vals, ("test@example.com",))

    def xtest_group_by(self):
        sql, vals = SqlBuilder.select(
            columns="id, COUNT(*)", table="users", groupby="id"
        )
        expected_sql = 'SELECT "id", COUNT(*) FROM "users" GROUP BY id'
        self.assertEqual(sql, expected_sql)
        self.assertEqual(vals, [])

    def xtest_order_by(self):
        sql, vals = SqlBuilder.select(
            columns="id, name", table="users", orderby="name DESC"
        )
        expected_sql = 'SELECT "id", "name" FROM "users" ORDER BY name DESC'
        self.assertEqual(sql, expected_sql)
        self.assertEqual(vals, [])

    def xtest_limit_offset(self):
        sql, vals = SqlBuilder.select(
            columns="id, name", table="users", start=10, qty=20
        )
        expected_sql = (
            'SELECT "id", "name" FROM "users" OFFSET 10 ROWS FETCH NEXT 20 ROWS ONLY'
        )
        self.assertEqual(sql, expected_sql)
        self.assertEqual(vals, [])

    def xtest_for_update(self):
        sql, vals = SqlBuilder.select(columns="id, name", table="users", lock=True)
        expected_sql = 'SELECT "id", "name" FROM "users" FOR UPDATE'
        self.assertEqual(sql, expected_sql)
        self.assertEqual(vals, [])

    def xtest_skip_locked(self):
        sql, vals = SqlBuilder.select(
            columns="id, name", table="users", skip_locked=True
        )
        expected_sql = 'SELECT "id", "name" FROM "users" FOR UPDATE SKIP LOCKED'
        self.assertEqual(sql, expected_sql)
        self.assertEqual(vals, [])

    def xtest_invalid_table(self):
        with self.assertRaises(Exception) as context:
            SqlBuilder.select(columns="id, name", table=None)
        self.assertTrue("Table name required" in str(context.exception))

    def xtest_missing_foreign_key(self):
        with self.assertRaises(exceptions.DbApplicationError) as context:
            SqlBuilder.select(
                columns=["profile>email"],
                table="users",
                tx=lambda table: None,  # Simulate missing foreign key
            )
        self.assertTrue("Foreign key not defined" in str(context.exception))


if __name__ == "__main__":
    unittest.main()
