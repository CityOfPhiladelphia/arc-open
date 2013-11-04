from xml.dom.minidom import parse


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

        self.fields.remove('Shape')
        self.fields.remove('FID')

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

    		self.markdown = self.markdown + '### Data Dictionary\n\n'
    		self.markdown = self.markdown + '| Field | Description  \n'
    		self.markdown = self.markdown + '| ----- | :----------:  \n'
    		for field in self.fields:
    				self.markdown = self.markdown + '| ' + field + '  \n'

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
            		self.markdown = self.markdown + '\n\n' + '### ' + title + '  \n\n'
            		self.markdown = self.markdown + content
            except:
            		pass

        self.markdown = self.markdown + '  \n\n'

        self._generate_data_dict()

        for section in self.bottom_sections:
            elem, title = section
            try:
            		content = self.source.getElementsByTagName(elem)[0]
            		content = content.firstChild.nodeValue
            		content = content.replace('\n', '  \n')
            		self.markdown = self.markdown + '\n\n' + '### ' + title + '  \n\n'
            		self.markdown = self.markdown + content
            except:
            		pass
        return self.markdown.encode('ascii', 'ignore')




