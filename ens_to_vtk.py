import vtk
import os
import sys
import numpy as np
import glob

def read_ens_file(ens_file, num_columns):
    with open(ens_file, 'r') as f:
        lines = f.readlines()
    data = []
    reading_data = False
    for line in lines:
        line = line.strip()
        if line.lower().startswith('part'):
            reading_data = True
            continue
        if reading_data and line:
            try:
                values = [float(val) for val in line.split()[:num_columns]]
                if len(values) == num_columns:
                    data.append(values)
                else:
                    print(f"Warning: Skipping line with incorrect number of values: {line}")
            except ValueError:
                print(f"Warning: Skipping non-numeric value: {line}")
    return np.array(data)

def ens_to_vtk(input_files, output_dir, num_columns, variable_names):
    try:
        print(f"VTK version: {vtk.vtkVersion.GetVTKVersion()}")
        
        case_file = next((f for f in input_files if f.lower().endswith('.case')), None)
        geo_file = next((f for f in input_files if f.lower().endswith('.geo')), None)
        ens_files = [f for f in input_files if f.lower().endswith('.ens')]
        
        if not (case_file and geo_file and ens_files):
            print("Error: Missing required files (.case, .geo, or .ens)")
            return False
        
        reader = vtk.vtkEnSightGoldReader()
        reader.SetCaseFileName(case_file)
        reader.UpdateInformation()
        reader.Update()
        
        output = reader.GetOutput()
        if output.IsA('vtkMultiBlockDataSet'):
            geometry = output.GetBlock(0)
        else:
            geometry = output
        
        if not geometry:
            print("Error: Unable to read geometry")
            return False
        
        for i, ens_file in enumerate(ens_files):
            print(f"Processing file: {ens_file}")
            data = read_ens_file(ens_file, num_columns)
            
            if len(data) == 0:
                print(f"Warning: No valid data found in {ens_file}")
                continue
            
            time_step_grid = vtk.vtkUnstructuredGrid()
            time_step_grid.ShallowCopy(geometry)
            
            for col, var_name in enumerate(variable_names):
                array = vtk.vtkFloatArray()
                array.SetName(var_name)
                array.SetNumberOfComponents(1)
                
                for j in range(min(len(data), time_step_grid.GetNumberOfPoints())):
                    array.InsertNextValue(data[j][col])
                
                for j in range(len(data), time_step_grid.GetNumberOfPoints()):
                    array.InsertNextValue(0.0)
                
                time_step_grid.GetPointData().AddArray(array)
            
            writer = vtk.vtkUnstructuredGridWriter()
            output_file = os.path.join(output_dir, f"output_{i:04d}.vtk")
            writer.SetFileName(output_file)
            writer.SetInputData(time_step_grid)
            writer.Write()
            
            print(f"Wrote file: {output_file}")
            for var_name in variable_names:
                array = time_step_grid.GetPointData().GetArray(var_name)
                print(f"{var_name} range: {array.GetRange()}")
        
        print(f"Conversion complete: {len(ens_files)} .ens files -> {output_dir}")
        return True
    except Exception as e:
        print(f"Error during conversion: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    input_files = ["path/to/your/file.case", "path/to/your/file.geo"] + glob.glob("path/to/your/*.ens")
    output_dir = "path/to/your/output_directory"
    num_columns = 3
    variable_names = ["Variable1", "Variable2", "Variable3"]
    ens_to_vtk(input_files, output_dir, num_columns, variable_names)
