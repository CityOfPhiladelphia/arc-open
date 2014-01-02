import arcpy, os, shutil
from arcpy import AddMessage, AddWarning, AddError
from export import Export
from esri2open import esri2open


class Convert(object):
    def __init__(self):
        self.label = 'Convert'
        self.description = 'Convert an ArcGIS feature class to open formats'
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define the parameters of the tool"""
        feature_class = arcpy.Parameter(
            name = 'in_features',
            displayName = 'In Features',
            direction = 'Input',
            datatype = 'GPFeatureLayer',
            parameterType = 'Required')

        field_mappings = arcpy.Parameter(
            name = 'in_fields',
            displayName = 'In Fields',
            direction = 'Input',
            datatype = 'GPFieldInfo',
            parameterType = 'Required')

        field_mappings.parameterDependencies = [feature_class.name]

        output_dir = arcpy.Parameter(
            name = 'output_dir',
            displayName = 'Output folder',
            direction = 'Input',
            datatype = 'DEFolder',
            parameterType = 'Required')

        output_name = arcpy.Parameter(
            name = 'output_name',
            displayName = 'Output filename',
            direction = 'Input',
            datatype = 'GPString',
            parameterType = 'Required')

        convert_4326 = arcpy.Parameter(
            name = 'convert_4326',
            displayName = 'Convert to WGS84?',
            direction = 'Input',
            datatype = 'GPBoolean',
            parameterType = 'Optional')
        convert_4326.value = 'True'

        convert_geojson = arcpy.Parameter(
            name = 'convert_geojson',
            displayName = 'Convert to GeoJSON?',
            direction = 'Input',
            datatype = 'GPBoolean',
            parameterType = 'Optional')
        convert_geojson.value = 'True'

        convert_kmz = arcpy.Parameter(
            name = 'convert_kmz',
            displayName = 'Convert to KMZ?',
            direction = 'Input',
            datatype = 'GPBoolean',
            parameterType = 'Optional')
        convert_kmz.value = 'True'

        convert_csv = arcpy.Parameter(
            name = 'convert_csv',
            displayName = 'Convert to CSV?',
            direction = 'Input',
            datatype = 'GPBoolean',
            parameterType = 'Optional')

        convert_metadata = arcpy.Parameter(
            name = 'convert_metadata',
            displayName = 'Convert metadata to markdown?',
            direction = 'Input',
            datatype = 'GPBoolean',
            parameterType = 'Optional')

        debug = arcpy.Parameter(
            name = 'debug',
            displayName = 'Debug',
            direction = 'Input',
            datatype = 'GPBoolean',
            parameterType = 'Optional')

        return [feature_class, field_mappings, output_dir, output_name,
                convert_4326, convert_geojson, convert_kmz, convert_csv,
                convert_metadata, debug]

    def isLicensed(self):
        return True

    def updateParameters(self, params):
        """Validate user input"""

        """
        If the input feature class is not point features, disable
        CSV export
        """
        if params[0].valueAsText:
            fc_type = arcpy.Describe(params[0].valueAsText).shapeType
            if fc_type in ['Point', 'MultiPoint']:
                params[7].enabled = 1
            else:
                params[7].enabled = 0

        return

    def checkFieldMappings(self, param):
        """
        Display warning message if any visible field is over 10 characters

        Args:
            param: the parameter that holds the field mappings
        """
        field_mappings = param.value
        over_fields = []
        fields_warning = ('The following visible field name(s) are' +
                         ' over 10 characters and will be shortened' +
                         ' automatically by ArcGIS: ')
        for idx, val in enumerate(range(field_mappings.count)):
            if field_mappings.getVisible(idx) == 'VISIBLE':
                field = field_mappings.getNewName(idx)
                if len(field) > 10:
                    over_fields.append(field)
        if over_fields:
            param.setWarningMessage(fields_warning + ", ".join(over_fields))
        else:
            param.clearMessage()

    def checkShapefileExists(self, dir, name):
        """Display error message if shapefile already exists.

        Args:
            dir: the output directory
            name: the output name
        """
        shapefile = dir.valueAsText + '\\shapefile\\' + name.valueAsText + '.shp'
        exists_error = ('A shapefile with this name already exists' +
                        ' in this directory. Either change the name ' +
                        'or directory or delete the previously created ' +
                        'shapefile.')
        if arcpy.Exists(shapefile):
            name.setErrorMessage(exists_error)
        else:
            name.clearMessage()


    def updateMessages(self, params):
        """Called after internal validation"""

        """
        Throws an error if a shapefile exists at the specified
        directory and file name
        """
        if params[2].value and params[2].altered:
            if params[3].value and params[3].altered:
                self.checkShapefileExists(params[2], params[3])

        """
        Throws a warning, not an error, if there is one or more visible
        output column names longer than 10 characters. ArcGIS will abbreviate
        these columns if they aren't changed or hidden. This behavior may be
        ok with the user, thus why we are only warning.
        """
        if params[1].value:
            self.checkFieldMappings(params[1])

        return

    def toBool(self, value):
            """Casts the user's input to a boolean type"""
            if value == 'true':
                return True
            else:
                return False

    def execute(self, parameters, messages):
        """Runs the script"""

        # Get the user's input
        fc = parameters[0].valueAsText
        field_mappings = parameters[1].valueAsText
        fields = parameters[1].valueAsText.split(';')
        fields.append('SHAPE@XY')
        output_dir = parameters[2].valueAsText
        output_name = parameters[3].valueAsText
        convert_to_wgs84 = self.toBool(parameters[4].valueAsText)
        convert_to_geojson = self.toBool(parameters[5].valueAsText)
        convert_to_kmz = self.toBool(parameters[6].valueAsText)
        convert_to_csv = self.toBool(parameters[7].valueAsText)
        convert_metadata = self.toBool(parameters[8].valueAsText)
        debug = self.toBool(parameters[9].valueAsText)

        # Setup vars
        output_path = output_dir + '\\' + output_name
        shp_output_path = output_dir + '\\shapefile'
        shp_temp_output_path = output_dir + '\\shapefile\\temp\\'
        shapefile = shp_output_path + '\\' + output_name + '.shp'
        temp_shapefile = shp_output_path + '\\temp\\' + output_name + '.shp'

        if debug:
            AddMessage('Field infos:')
            AddMessage(field_mappings)

        try:
            arcpy.Delete_management('temp_layer')
        except:
            if debug:
                AddMessage('Did not have a temp_layer feature ' +
                                    'class to delete')

        if not os.path.exists(shp_output_path):
            os.makedirs(shp_output_path)
            if debug:
                AddMessage('Created directory ' + shp_output_path)

        if not os.path.exists(shp_temp_output_path):
            os.makedirs(shp_temp_output_path)
        else:
            for file in os.listdir(shp_temp_output_path):
                file_path = os.path.join(shp_temp_output_path, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except:
                    AddWarning('Unable to delete ' + file +
                                      'from the temp folder. This ' +
                                      'may become a problem later')
                    pass

        arcpy.MakeFeatureLayer_management(fc, 'temp_layer', '', '',
                                          field_mappings)
        arcpy.CopyFeatures_management('temp_layer', temp_shapefile)

        if convert_to_wgs84:
            AddMessage('Converting spatial reference to WGS84...')
            arcpy.Project_management(temp_shapefile, shapefile, "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433],METADATA['World',-180.0,-90.0,180.0,90.0,0.0,0.0174532925199433,0.0,1262]]", "WGS_1984_(ITRF00)_To_NAD_1983", "PROJCS['NAD_1983_StatePlane_Pennsylvania_South_FIPS_3702_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',1968500.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-77.75],PARAMETER['Standard_Parallel_1',39.93333333333333],PARAMETER['Standard_Parallel_2',40.96666666666667],PARAMETER['Latitude_Of_Origin',39.33333333333334],UNIT['Foot_US',0.3048006096012192]]")
            AddMessage('Projection conversion completed.')
        else:
            AddMessage('Exporting shapefile already in WGS84...')
            arcpy.FeatureClassToShapefile_conversion(temp_shapefile,
                                                     shp_output_path)

        try:
            arcpy.Delete_management('temp_layer')
        except:
            AddError('Unable to delete in_memory feature class')

        AddMessage('Compressing the shapefile to a .zip file...')

        export = Export(output_dir, output_name, debug)

        zip = export.zip()
        if zip:
            AddMessage('Finished creating ZIP archive')

        if convert_to_geojson:
            AddMessage('Converting to GeoJSON...')
            output = output_path + '.geojson'
            geojson = esri2open.toOpen(shapefile, output,
                                       includeGeometry='geojson')
            if geojson:
                AddMessage('Finished converting to GeoJSON')

        if convert_to_kmz:
            AddMessage('Converting to KML...')
            kmz = export.kmz()
            if kmz:
                AddMessage('Finished converting to KMZ')

        if convert_to_csv:
            AddMessage('Converting to CSV...')
            csv = export.csv()
            if csv:
                AddMessage('Finished converting to CSV')

        if convert_metadata:
            AddMessage('Converting metadata to Markdown ' +
                                'README.md file...')
            md = export.md()
            if md:
                AddMessage('Finished converting metadata to ' +
                                    'Markdown README.md file')

        # Delete the /temp directory because we're done with it
        shutil.rmtree(shp_output_path + '\\temp')
        if (debug):
            AddMessage('Deleted the /temp folder because we don\'t' +
                                ' need it anymore')

        return