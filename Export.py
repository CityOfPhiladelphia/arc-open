from arcpy import AddMessage, AddErrorMessage
import arcpy, csv, os, zipfile, glob, copy
from xml.dom.minidom import parse


class CSV:

    def __init__(self, output_path, shapefile):
        self.shapefile = shapefile
        self.shapefile_desc = arcpy.Describe(shapefile)
        self.shapefile_type = self.shapefile_desc.shapeType
        self.output_path = output_path
        self.fields = [i.name for i in arcpy.ListFields(self.shapefile)]

    def __str__(self):
        return 'ArcOpen CSV class'

    def generate(self):
        try:
            if self.shapefile_type in ['Point', 'MultiPoint']:
                with open(self.output_path + '.csv', 'wb') as f:
                    writer = csv.writer(f)
                    try:
                        self.fields.remove('Shape')
                        self.fields.remove('FID')
                    except:
                        pass
                    headers = copy.deepcopy(self.fields)
                    self.fields.append('SHAPE@XY')
                    headers.extend(['LAT', 'LNG'])
                    writer.writerow(headers)
                    cur = arcpy.SearchCursor(self.shapefile)
                    with arcpy.da.SearchCursor(self.shapefile, self.fields) as cur:
                        for row in cur:
                            row = row[0:-1] + row[-1]
                            writer.writerow(row)
                    return True

            else:
                AddMessage('Sorry, converting layers of geometry type ' + self.shapefile_type + ' is not supported.')
                return False

        except Exception as err:
            AddErrorMessage('Unable to export CSV file: ' + str(err))
            return False


class ZIP:

    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.compression = zipfile.ZIP_DEFLATED
        self.match = self.path + '\\' + self.name + '.*'
        self.zip_file = self.path + '\\' + self.name + '.zip'

    def __str__(self):
        return 'ArcOpen ZIP class'

    def generate(self):
        files = glob.glob(self.match)
        zf = zipfile.ZipFile(self.zip_file, mode='w')
        for file in files:
            try:
                zf.write(file, compress_type=self.compression, arcname=os.path.basename(file))
            except:
                AddMessage('Could not include ' + file + ' in .zip archive!')
                return False
        zf.close()
        return True


class KMZ:

    def __init__(self, name, shapefile, path):
        self.shapefile = shapefile
        self.name = name
        self.path = path
        self.output = path + '.kmz'

    def generate(self):
        arcpy.MakeFeatureLayer_management(self.shapefile, self.name)
        if arcpy.Exists(self.output):
            arcpy.Delete_management(self.output)
        try:
            arcpy.LayerToKML_conversion(self.name, self.output, '', '', self.name, '1024', '96', 'CLAMPED_TO_GROUND')
            return True
        except Exception as err:
            AddErrorMessage('Unable to export KMZ file: ' + str(err))
            return False

class Markdown:

    def __init__(self, xml_file, fields):
        self.input = xml_file
        self.source = self._load(self.input)
        self.markdown = ''
        self.fields = fields
        self.top_sections = [
            ('abstract', 'Description'),
            ('purpose', 'Summary')
        ]
        self.bottom_sections = [
            ('datacred', 'Credits'),
            ('useconst', 'Use Limitations')
        ]
        try:
            self.fields.remove('Shape')
            self.fields.remove('FID')
        except:
            pass

    def __str__(self):
        return 'ArcOpen Markdown class'

    def _load(self, xml_file):
        xmldoc = parse(xml_file).documentElement
        return xmldoc

    def _generate_title(self, xml):
        title = xml.getElementsByTagName('title')[0]
        title = title.firstChild.nodeValue
        md = self._printHeader(title)
        return md

    def _generate_data_dict(self):

        self.markdown += '### Data Dictionary\n\n'
        self.markdown += '| Field | Description  \n'
        self.markdown += '| ----- | :----------:  \n'
        for field in self.fields:
            self.markdown += '| ' + field + ' |  \n'

    def _printHeader(self, text):
        return '# ' + text

    def generate(self):
        self.markdown = self._generate_title(self.source)
        for section in self.top_sections:
            elem, title = section
            try:
                content = self.source.getElementsByTagName(elem)[0]
                content = content.firstChild.nodeValue
                content = content.replace('\n', '  \n')
                self.markdown += '\n\n' + '### ' + title + '  \n\n'
                self.markdown += content
            except:
                pass

        self.markdown += '  \n\n'

        self._generate_data_dict()

        for section in self.bottom_sections:
            elem, title = section
            try:
                content = self.source.getElementsByTagName(elem)[0]
                content = content.firstChild.nodeValue
                content = content.replace('\n', '  \n')
                self.markdown += '\n\n' + '### ' + title + '  \n\n'
                self.markdown += content
            except:
                pass
        return self.markdown.encode('ascii', 'ignore')




