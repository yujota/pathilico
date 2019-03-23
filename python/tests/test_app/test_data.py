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


class TestAddRecordToTableModel(unittest.TestCase):

    def createTableModel(self, headers, types):
        from pathilico.app.data import TableModel
        return TableModel(headers, types)

    def getAddRecordFunc(self):
        from pathilico.app.data import add_record_to_table as f
        return f

    def getDeleteRecordFunc(self):
        from pathilico.app.data import delete_record_from_table as f
        return f

    def getGetRecordsFromTable(self):
        from pathilico.app.data import get_records_from_table as f
        return f

    def testAddRecord(self):
        table = self.createTableModel(("a", "b", "c"), ("int", "int", "int"))
        add_record = self.getAddRecordFunc()
        mock_id = b"\x04"
        mock_record = (123, 234, 245)
        self.assertEqual(0, len(table.table_rows))
        table = add_record(table, mock_id, mock_record)
        self.assertEqual(1, len(table.table_rows))

    def testDeleteRecord(self):
        table = self.createTableModel(("a", "b", "c"), ("int", "int", "int"))
        add_record = self.getAddRecordFunc()
        delete_record = self.getDeleteRecordFunc()
        mock_id = b"\x04"
        mock_record = (123, 234, 245)
        table = add_record(table, mock_id, mock_record)
        self.assertEqual(1, len(table.table_rows))
        table = delete_record(table, mock_id)
        self.assertEqual(0, len(table.table_rows))

    def testGetRecords(self):
        table = self.createTableModel(("a", "b", "c"), ("int", "int", "int"))
        add_record = self.getAddRecordFunc()
        get_records = self.getGetRecordsFromTable()
        mock_id = b"\x04"
        mock_record = (123, 234, 245)
        table = add_record(table, mock_id, mock_record)
        actual_ids, actual_records = get_records(table, [mock_id])
        self.assertEqual((mock_record, ), actual_records)
        self.assertEqual((mock_id, ), actual_ids)
