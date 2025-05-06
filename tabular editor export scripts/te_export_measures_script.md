// Tabular Editor C Script to retrieve all Measures and export as .tsv


// Get all visible measures only
var measures = Model.AllMeasures
    .Where(m => !m.IsHidden && !m.Table.IsHidden);

// Export the required properties to TSV
var tsv = ExportProperties(measures, "Name,ObjectType,Parent,DisplayFolder,Description,FormatString,DataType,Expression");

// Set filename based on the model name
var filename = string.Format(@"C:\dev\{0}_export_documentation.tsv", Model.D);

// Save the TSV to a file
SaveFile(filename, tsv);
