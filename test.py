import unittest
import main
import datetime

class TestMain(unittest.TestCase):
    def test_open_driver(self):
        try:
            self.driver = main.open_driver()
            self.assertEqual(self.driver.title, 'Bus Times - BusRoutes', 'TEST FAILED: Driver did not open correctly')
            print('TEST PASSED: Driver opened correctly')
        except AssertionError as e:
            print(e)
    def test_select_bus_route(self):
        try:
            self.driver = main.open_driver()
            _, self.select = main.select_bus_route(self.driver)
            self.assertEqual(self.select.first_selected_option.text, '40 Century Tree', 'TEST FAILED: Bus route was not selected correctly')
            print('TEST PASSED: Bus route was selected correctly')
        except AssertionError as e:
            print(e)
    def test_scrape_times(self):
        try:
            self.driver, self.table_rows = main.scrape_times()
            self.assertNotEqual(len(self.table_rows), 0, 'TEST FAILED: Table rows were not scraped correctly')
            print('TEST PASSED: Table rows were scraped correctly')
        except AssertionError as e:
            print(e)
    def test_available_bus_times(self):
        try:
            self.driver, self.table_rows = main.scrape_times()
            self.msc_times, self.holleman_south_times = main.available_bus_times(self.driver, self.table_rows)
            self.assertNotIn('PastLeaveTime', self.msc_times, 'TEST FAILED: MSC times were not scraped correctly')
            self.assertNotIn('PastLeaveTime', self.holleman_south_times, 'TEST FAILED: Holleman South times were not scraped correctly')
            print('TEST PASSED: MSC times were scraped correctly')
            print('TEST PASSED: Holleman South times were scraped correctly')
        except AssertionError as e:
            print(e)
    def test_find_earliest_bus(self):
        try:
            self.driver, self.table_rows = main.scrape_times()
            self.msc_times, self.holleman_south_times = main.available_bus_times(self.driver, self.table_rows)
            self.earliest_bus = main.find_earliest_bus(self.msc_times)
            now = datetime.datetime.now()
            now = now.strftime("%I:%M %p")
            print(self.earliest_bus, now)
            self.assertNotEqual(self.earliest_bus, now, 'TEST FAILED: Earliest bus was not found correctly')
            print('TEST PASSED: Earliest bus was found correctly')
        except AssertionError as e:
            print(e)


if __name__ == '__main__':
    unittest.main()
