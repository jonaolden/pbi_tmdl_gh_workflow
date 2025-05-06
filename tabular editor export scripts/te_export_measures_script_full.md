// Get model name
var reportName = Model.Name;

// TSV header
var lines = new List<string>();
lines.Add("Measure Name\tDescription\tDAX Code\tReport Name\tSource Table\tReferenced Tables");

// Sanitization function for TSV
Func<string, string> clean = s => 
    (s ?? "")
    .Replace("\t", " ")     // Replace tabs with space
    .Replace("\r", " ")     // Remove carriage returns
    .Replace("\n", " ")     // Remove line feeds
    .Trim();

// Extract referenced table names from expression
Func<string, List<string>> extractTableNames = expr => {
    var tableNames = new HashSet<string>();
    foreach (var table in Model.Tables.Where(t => !t.IsHidden))
    {
        if (!string.IsNullOrEmpty(table.Name) && expr.IndexOf(table.Name + "[", StringComparison.OrdinalIgnoreCase) >= 0)
        {
            tableNames.Add(table.Name);
        }
    }
    return tableNames.OrderBy(n => n).ToList();
};

// Process each visible measure
foreach (var measure in Model.AllMeasures.Where(m => !m.IsHidden && !m.Table.IsHidden))
{
    var referencedTables = extractTableNames(measure.Expression);
    var line = string.Join("\t", new[] {
        clean(measure.Name),
        clean(measure.Description),
        clean(measure.Expression),
        clean(reportName),
        clean(measure.Table.Name),
        clean(string.Join(";", referencedTables))
    });

    lines.Add(line);
}

// Save output
SaveFile(@"C:\dev\measures_metadata.tsv", string.Join("\n", lines));
