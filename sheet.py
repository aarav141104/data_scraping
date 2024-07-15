import pandas as pd


file_path = "461976150-Karnataka-RERA-List-of-approved-Agents.xlsx"
excel_file = pd.ExcelFile(file_path)

combined_df = pd.DataFrame()
for sheet in excel_file.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet)
    combined_df = pd.concat([combined_df, df], ignore_index=True)

# Reset the index and remove unnecessary columns or rows if needed
combined_df.reset_index(drop=True, inplace=True)

# Optional: Drop columns with all NaN values
combined_df.dropna(axis=1, how="all", inplace=True)

# Save the combined DataFrame to a new Excel file
output_file_path = "karnataka.xlsx"
combined_df.to_excel(output_file_path, index=False)
