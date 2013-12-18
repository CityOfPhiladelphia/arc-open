# ArcOpen  

ArcOpen is an ArcGIS Desktop Python toolbox that makes exporting ArcGIS feature classes to open geodata formats (GeoJSON, KML, CSV and shapefile, compressed and uncompressed) a breeze. It'll even create a Markdown `README.md` file for you from your layer's metadata! We (City of Philadelphia) use it to quickly publish our geodata to GitHub.

Special thanks to [Project Open Data](https://github.com/project-open-data)'s for [esri2open](https://github.com/project-open-data/esri2open) which is used for creating the GeoJSON.  

**Runs on ArcGIS 10.1+**

### Installation

There are a few ways that the toolbox can be installed besides the regular `git clone\fork`

* If you are using ArcGIS 10.1, [download the ZIP archive of the source code](https://github.com/CityOfPhiladelphia/arc-open/archive/v1.0.zip) and extract it somewhere on your machine. In Desktop or Catalog, open the ArcToolbox window and add the `arc-open/arc_open/esri/toolboxes/ArcOpen.pyt` file as a new toolbox.  

Please do not add the toolbox in your ArcToolbox and save the settings to the default location, *this may be cause ArcGIS to crash on future launches*! If you do this anyway, navigate to `%APPDATA%\Roaming\ESRI\Desktop10.x\ArcToolbox` and rename the `ArcToolbox.dat` file. On next launch of the application it should recreate this file with the factory settings. Perhaps there's a way around this but we haven't found one yet. You have been warned!

* If you're using ArcGIS 10.2, it's a lot easier for you. Simply [download the .exe installer](https://github.com/CityOfPhiladelphia/arc-open/releases/download/v1.0/ArcOpen-1.0.0.exe) and run it to install the toolbox as a Python module (using Python's [Distutils](http://blogs.esri.com/esri/arcgis/2013/08/13/extending-geoprocessing-through-python-modules/)). The toolbox is now automagically added as a new System Toolbox.

### Usage

Once the toolbox is loaded into ArcGIS Desktop or Catalog, expand the "ArcOpen" toolbox and double-click the "Convert" tool like you would do with any other tool. The parameters in the resulting tool window are:

1. **In Features**: The input feature class you want to export
2. **In Fields**: Here you can select/deselect the fields that you want included in the export and even change their names. Object ID and Shape fields will be included in the shapefile export but if you don't select them here (and you shouldn't), they won't be included in the other export formats.
3. **Output folder**: As you may have guessed, the output folder of your exported files
4. **Output filename**: The filename of all of your exported files (see the output structure below)
5. **Export options**: All of these are optional. If your input feature class is not made of point features, you won't be able to export a CSV since it doesn't make sense to include a geometry in a CSV if it isn't a latitude/longitude pair (in our opinion).

The tool will export the requested files in the following structure:

    \OutputDir
        | OutputName.geojson
        | OutputName.kmz
        | OutputName.csv
        | README.md
        \ shapefile
            | OutputName.dbf
            | OutputName.prj
            | OutputName.sbn
            | OutputName.sbx
            | OutputName.shp
            | OutputName.shp.xml
            | OutputName.shx
            | OutputName.zip

**A note about metadata**: the tool uses the `ARCGIS2FGDC.xml` translator XML file included with ArcGIS installs to pull out the "Summary", "Description", "Credits" and "Use Limitations" sections of your metadata. It also adds a "Data Dictionary" section to the exported `README.md` file with the beginnings of a Markdown table of your exported fields for you to finish. You will mostly definitely need to edit your `README.md` before publishing as the export is not perfect.  

You can also use the tool from within a Python script:

```python
Convert_ArcOpen(in_features, in_fields, output_dir, output_name, {convert_4326}, {convert_geojson}, {convert_kmz}, {convert_csv}, {convert_metadata}, {debug})
```
For example:  

```python
import arcpy
# You'll have to import it into the arcpy namespace first
arcpy.ImportToolbox('path/to/ArcOpen.pyt') 
Convert_ArcOpen('path/or/db/connection/to/farmers_markets',
                'OBJECTID OBJECTID HIDDEN NONE;
                NAME NAME VISIBLE NONE;
                ADDRESS ADDRESS VISIBLE NONE;
                OPERATOR OPERATOR VISIBLE NONE;
                ACCEPT_SNA SNA VISIBLE NONE;
                ACCEPT_FMN FMN VISIBLE NONE;
                DISTRIBUTE DISTRIBUTE VISIBLE NONE;
                ONLY_REDEE REDEEM VISIBLE NONE;
                EBT_MACHIN EBT VISIBLE NONE;
                DAY_TIME DAY_TIME VISIBLE NONE;
                ZIP_CODE ZIP_CODE VISIBLE NONE;
                SHAPE SHAPE HIDDEN NONE',
                'c:/github_data', 'farmers_markets', 'true', 'true',
                'true', 'true', 'true', 'false'))
```

### Development

If you make changes and want to rebuild the installer, run this in the root of the project:

    python setup.py bdist_wininst

### Issues
Questions or ideas? Feel free to [submit an issue](https://github.com/CityOfPhiladelphia/arc-open/issues/new). If you're thinking about submitting a pull request, talk to us first because we can't guarantee that we'll accept every pull request because if it doesn't meet our requirements for this tool. With that being said, please feel free to fork and edit as you'd like.