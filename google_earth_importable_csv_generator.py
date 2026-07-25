# Copyright 2026 NorCalRobotics
# Unmodified use and code review only. No AI/ML training or redistribution rights.

class CsvGenerator:
    def __init__(self, csv_output_filename):
        self.output_csv = open(csv_output_filename, 'w')
        self.output_csv.write('Latitude,Longitude,Name\n')

    def add_placemark(self, photo_path, latitude, longitude):
        self.output_csv.write('%s,%s,%s\n' % (latitude, longitude, photo_path))
