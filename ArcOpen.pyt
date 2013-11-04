import arcpy, os, shutil
import Metadata, Export
from esri2open import esri2open

reload(Metadata)
reload(Export)
reload(esri2open)


class Toolbox(object):
    def __init__(self):
        self.label = 'ArcOpen'
        self.alias = 'ArcOpen'
        self.tools = [Convert]


class Convert(object):
    def __init__(self):
        self.label = 'Convert'
        self.description = 'Convert an ArcGIS feature class to GeoJSON, KMZ and CSV'
        self.canRunInBackground = False

    def getParameterInfo(self):
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
            datatype = 'Field',
            parameterType = 'Required',
            multiValue = True)

        field_mappings.filter.list = ['Short', 'Long', 'Float', 'Single', 'Double', 'Text', 'Date', 'String']
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
            datatype = 'Boolean',
            parameterType = 'Optional')

        convert_geojson = arcpy.Parameter(
            name = 'convert_geojson',
            displayName = 'Convert to GeoJSON?',
            direction = 'Input',
            datatype = 'Boolean',
            parameterType = 'Optional')

        convert_kmz = arcpy.Parameter(
            name = 'convert_kmz',
            displayName = 'Convert to KMZ?',
            direction = 'Input',
            datatype = 'Boolean',
            parameterType = 'Optional')

        convert_csv = arcpy.Parameter(
            name = 'convert_csv',
            displayName = 'Convert to CSV?',
            direction = 'Input',
            datatype = 'Boolean',
            parameterType = 'Optional')

        convert_metadata = arcpy.Parameter(
            name = 'convert_metadata',
            displayName = 'Convert metadata to markdown?',
            direction = 'Input',
            datatype = 'Boolean',
            parameterType = 'Optional')

        debug = arcpy.Parameter(
            name = 'debug',
            displayName = 'Debug',
            direction = 'Input',
            datatype = 'Boolean',
            parameterType = 'Optional')

        return [feature_class, field_mappings, output_dir, output_name,
                convert_4326, convert_geojson, convert_kmz, convert_csv,
                convert_metadata, debug]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        fc_type = arcpy.Describe(parameters[0].valueAsText).shapeType
        if fc_type in ['Point', 'MultiPoint']:
            parameters[7].enabled = 1
        else:
            parameters[7].enabled = 0

    def execute(self, parameters, messages):
        fc = parameters[0].valueAsText
        fields = parameters[1].valueAsText.split(';')
        fields.append('SHAPE@XY')
        output_dir = parameters[2].valueAsText
        output_name = parameters[3].valueAsText
        convert_to_wgs84 = bool(parameters[4].valueAsText)
        convert_to_geojson = bool(parameters[5].valueAsText)
        convert_to_kmz = bool(parameters[6].valueAsText)
        convert_to_csv = bool(parameters[7].valueAsText)
        convert_metadata = bool(parameters[8].valueAsText)
        debug = bool(parameters[9].valueAsText)

        output_path = output_dir + '\\' + output_name
        shp_output_path = output_dir + '\\shapefile'
        shp_temp_output_path = output_dir + '\\shapefile\\temp\\'
        shapefile = shp_output_path + '\\' + output_name + '.shp'
        temp_shapefile = shp_output_path + '\\temp\\' + output_name + '.shp'

        if debug:
            messages.addMessage('Fields selected:')
            messages.addMessage(fields)

        try:
            arcpy.Delete_management('temp_layer')
        except:
            if debug:
                messages.addMessage('Did not have a temp_layer feature class to delete')

        if not os.path.exists(shp_output_path):
            os.makedirs(shp_output_path)
            if debug:
                messages.addMessage('Created directory ' + shp_output_path)

        if not os.path.exists(shp_temp_output_path):
            os.makedirs(shp_temp_output_path)
        else:
            for file in os.listdir(shp_temp_output_path):
                file_path = os.path.join(shp_temp_output_path, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except:
                    messages.addWarningMessage('Unable to delete ' + file + 'from the temp folder. This may become a problem later')
                    pass

        all_fields = [i.name for i in arcpy.ListFields(fc)]
        to_delete = [x for x in all_fields if x not in set(fields)]
        # TODO: Refactor this - should be able to remove the below attrbutes from a list more elegantly
        to_not_delete = ['OBJECTID', 'SHAPE']
        for field in to_not_delete:
            try:
                to_delete.remove(field)
            except:
                pass
        if debug:
            messages.addMessage('Fields that must be deleted from output:')
            messages.addMessage(to_delete)
        field_info = ''
        for field in to_delete:
            field_info = field_info + ''.join([field, ' ', field, ' ', 'HIDDEN ', 'NONE; '])

        arcpy.MakeFeatureLayer_management(fc, 'temp_layer', '', '', field_info)
        arcpy.CopyFeatures_management('temp_layer', temp_shapefile)

        if convert_to_wgs84:
            messages.addMessage('Converting spatial reference to WGS84...')
            arcpy.Project_management(temp_shapefile, shapefile, "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433],METADATA['World',-180.0,-90.0,180.0,90.0,0.0,0.0174532925199433,0.0,1262]]", "WGS_1984_(ITRF00)_To_NAD_1983", "PROJCS['NAD_1983_StatePlane_Pennsylvania_South_FIPS_3702_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',1968500.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-77.75],PARAMETER['Standard_Parallel_1',39.93333333333333],PARAMETER['Standard_Parallel_2',40.96666666666667],PARAMETER['Latitude_Of_Origin',39.33333333333334],UNIT['Foot_US',0.3048006096012192]]")
            messages.addMessage('Projection conversion completed.')
        else:
            messages.addMessage('Exporting shapefile already in WGS84...')
            arcpy.FeatureClassToShapefile_conversion(temp_shapefile, shp_output_path)

        try:
            arcpy.Delete_management('temp_layer')
        except:
            messages.addMessage('Unable to delete in_memory feature class')

        messages.addMessage('Compressing the shapefile to a .zip file...')
        zip = Export.ZIP(shp_output_path, output_name).generate()
        if zip:
            messages.addMessage('Finished creating .zip file')

        if convert_to_geojson:
            messages.addMessage('Converting to GeoJSON...')
            output = output_path + '.geojson'
            geojson = esri2open.toOpen(shapefile, output, includeGeometry='geojson')
            if geojson:
                messages.addMessage('Finished creating .geojson file')

        if convert_to_kmz:
            messages.addMessage('Converting to KML...')
            kmz = Export.KMZ(output_name, shapefile, output_path).generate()
            if kmz:
                messages.addMessage('Finished creating KMZ file')

        if convert_to_csv:
            messages.addMessage('Converting to CSV...')
            csv_file = Export.CSV(output_path, shapefile).generate()
            if csv_file:
                messages.addMessage('Finished creating .csv file')

        if convert_metadata:
            messages.addMessage('Converting metadata to Markdown README.md file...')
            install_dir = arcpy.GetInstallInfo('desktop')['InstallDir']
            if debug:
                messages.addMessage('ArcGIS install directory: ' + install_dir)
            translator = install_dir + 'Metadata\\Translator\\ARCGIS2FGDC.xml'
            if (debug):
                messages.addMessage('Using the XML translator at ' + translator)
            output = shp_output_path + '\\temp\\' + 'README.xml'
            arcpy.ESRITranslator_conversion(shapefile, translator, output)
            attributes = [i.name for i in arcpy.ListFields(shapefile)]
            md = Metadata.Markdown(output, attributes).generate()
            md_file = open(output_dir + '\\README.md', 'w')
            messages.addMessage('Open output markdown file: ' + str(md_file))
            try:
                md_file.write(md)
                messages.addMessage('Finished creating .md file')
            except Exception as err:
                messages.addMessage('Error creating Markdown metadata file: ' + str(err))
            finally:
                md_file.close()

        # Delete the /temp directory because we're done with it
        shutil.rmtree(shp_output_path + '\\temp')
        if (debug):
            messages.addMessage('Deleted the /temp folder because we don\'t need it anymore')

        return
