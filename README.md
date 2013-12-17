# ArcOpen  

ArcOpen is an ArcGIS Desktop Python toolbox that makes exporting ArcGIS feature classes to open geodata formats (GeoJSON, KML, CSV and more) a breeze. It'll even create a Markdown `README.md` file for you from your layer's metadata! We (City of Philadelphia) use it to quickly publish our geodata to GitHub.

Special thanks to [Project Open Data](https://github.com/project-open-data)'s for [esri2open](https://github.com/project-open-data/esri2open) which is used for creating the GeoJSON.  

**Runs on ArcGIS 10.1+**

### Installation

There are a few ways that the toolbox can be installed besides the regular `git clone\fork`

* If you are using ArcGIS 10.1, [download the ZIP archive of the source code](https://github.com/CityOfPhiladelphia/arc-open/archive/v1.0.zip) and extract it somewhere on your machine. Copy the resulting folder to `%APPDATA%\Roaming\ESRI\Desktop10.x\ArcToolbox\My Toolboxes` so that it is available through Catalog anytime you need it.  

* If you're using ArcGIS 10.2, it's a lot easier for you. Simply [download the .exe installer](https://github.com/CityOfPhiladelphia/arc-open/releases/download/v1.0/ArcOpen-1.0.0.exe) and run it to install the toolbox as a Python module (using Python's [Distutils](http://blogs.esri.com/esri/arcgis/2013/08/13/extending-geoprocessing-through-python-modules/)). The toolbox is now automagically added as a new System Toolbox.

Please do not add the toolbox in your ArcToolbox and save the settings to the default location, *this may be cause ArcGIS to crash on future launches*! If you do this anyway, navigate to `%APPDATA%\Roaming\ESRI\Desktop10.x\ArcToolbox` and rename the `ArcToolbox.dat` file. On next launch of the application it should recreate this file with the factory settings. Perhaps there's a way around this but we haven't found one yet. You have been warned.

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

You can also use the tool from within a Python script. If the toolbox is loaded into your Python folder (through the ArcToolbox window or if you've copied it to the `%APPDATA%\Roaming\ESRI\Desktop10.1\ArcToolbox\My Toolboxes` directory on your machine) you can call it with:

    Convert_ArcOpen (in_features, in_fields, output_dir, output_name, {convert_4326}, {convert_geojson}, {convert_kmz}, {convert_csv}, {convert_metadata}, {debug})

### Issues
Questions or requests? Feel free to [submit an issue](https://github.com/CityOfPhiladelphia/arc-open/issues/new). If you're thinking about submitting a pull request, talk to us first because we can't guarantee that we'll accept every pull request because if it doesn't meet our requirements for this tool. With that being said, please feel free to fork and edit as you'd like.

### License

Copyright (c) 2013, City of Philadelphia All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
* Neither the name of the City of Philadelphia nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.  

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.