from unittest import TestCase
import Wallscraper


class TestWallScraper(TestCase):

    def test_check_file_ext(self):
        scrape = Wallscraper.WallScraper()
        print scrape.check_file_ext(file_loc=r'C:\wallbase\searches\Toplist\SKETCHY\wallhaven-9456.jpg', ext_list=['jpg', 'png'])

