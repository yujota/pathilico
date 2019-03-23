#   Copyright
#     2019 Department of Dermatology, School of Medicine, Tohoku University
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import unittest


class TestCreateTable(unittest.TestCase):

    def createDatabaseObject(self):
        from pathilico.app.ports.pickle_database import create_database_object
        return create_database_object()

    def getCreateNewTableFunc(self):
        from pathilico.app.ports.pickle_database \
            import create_new_table as f
        return f

    def getHasTableFunc(self):
        from pathilico.app.ports.pickle_database \
            import has_table as f
        return f

    def testCreateTable(self):
        db = self.createDatabaseObject()
        create_new_table = self.getCreateNewTableFunc()
        has_table = self.getHasTableFunc()
        self.assertFalse(has_table(db, "hoge"))
        db = create_new_table(
            db, "hoge", ("a", "b", "c"), ("b", )
        )
        self.assertTrue(has_table(db, "hoge"))


class TestGetRecord(unittest.TestCase):
    def createDatabaseObject(self):
        from pathilico.app.ports.pickle_database import create_database_object
        return create_database_object()

    def getCreateNewTableFunc(self):
        from pathilico.app.ports.pickle_database \
            import create_new_table as f
        return f

    def getAddRecordFunc(self):
        from pathilico.app.ports.pickle_database \
            import add_record as f
        return f

    def getGetAllRecords(self):
        from pathilico.app.ports.pickle_database \
            import get_all_records as f
        return f

    def getDeleteRecord(self):
        from pathilico.app.ports.pickle_database \
            import delete_record as f
        return f

    def testAddRecord(self):
        db = self.createDatabaseObject()
        create_new_table = self.getCreateNewTableFunc()
        add_record = self.getAddRecordFunc()
        get_all_records = self.getGetAllRecords()
        delete_record = self.getDeleteRecord()

        mock_table_name = "Mock"
        mock_header = ("a", "b")
        mock_type = ("str", "str")
        db = create_new_table(db, mock_table_name, mock_header, mock_type)

        mock_record_id = 134
        mock_record = (1, 2)
        ids, recs = get_all_records(db, mock_table_name)
        self.assertEqual(0, len(recs))
        db = add_record(db, mock_table_name, mock_record_id, mock_record)
        ids, recs = get_all_records(db, mock_table_name)
        self.assertEqual(1, len(recs))

        db = delete_record(db, mock_table_name, mock_record_id)
        ids, recs = get_all_records(db, mock_table_name)
        self.assertEqual(0, len(recs))



