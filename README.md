# SciBlend: ENStoVTK

ENStoVTK is a Python tool with a web interface for converting Ensight files (.ens, .case, .geo) to VTK format (.vtk). This tool facilitates the conversion of Ensight simulation data to a more widely used format in scientific visualization.

## Features

- Intuitive web interface for uploading files and configuring the conversion
- Support for multiple .ens files
- Conversion of .case, .geo, and .ens files to .vtk format
- Custom specification of variable names for each data column
- Automatic download of converted files in a ZIP archive

## Requirements

- Python 3.x
- VTK library (tested with version 9.3.1)
- Flask

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/SciBlend-ENStoVTK.git
   cd SciBlend-ENStoVTK
   ```

2. Install the required dependencies:
   ```
   pip install vtk==9.3.1 flask
   ```

   Note: If you encounter issues, try different versions of VTK.

## Usage

1. Start the Flask application:
   ```
   python app.py
   ```

2. Open a web browser and go to `http://localhost:5001`

3. Follow the instructions on the web interface:
   - Upload a .case file containing the simulation setup
   - Upload a .geo file containing the geometry information
   - Upload one or more .ens files containing the simulation data
   - Specify the number of data columns in your .ens files
   - Provide names for each data column (variable)
   - Click "Convert" to process your files

4. Download the resulting ZIP file containing the converted .vtk files

## File Structure

- `ens_to_vtk.py`: Contains the conversion logic
- `app.py`: Flask application for the web interface
- `templates/upload.html`: HTML template for the web interface
- `uploads/`: Temporary storage for uploaded Ensight files
- `outputs/`: Storage for converted .vtk files

## Troubleshooting

If you encounter issues:
1. Verify that VTK is installed correctly
2. Ensure your input files are in the correct Ensight format
3. Check the server logs for detailed error messages
4. If the conversion seems to complete but no file is downloaded, check the 'outputs' folder

## Contributing

Contributions are welcome. Please open an issue to discuss major changes before submitting a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.