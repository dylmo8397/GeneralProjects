import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "/Users/dylanmorgan/Documents/ChatGPT/MSBX 5460 - Supply Chain Strategy Class Note/outputs/01a06912-5c8c-70f2-b6ea-a4e9152436f9";
const outputPath = `${outputDir}/MAD_MSE_Arithmetic_Mean.xlsx`;
const previewPath = "/private/tmp/MAD_MSE_Arithmetic_Mean_preview.png";

const workbook = Workbook.create();
const sheet = workbook.worksheets.add("Arithmetic Mean");
sheet.showGridLines = false;

const fontFamily = "Arial";
const titleColor = "#5C5572";
const headerFill = "#6F658C";
const headerText = "#FFFFFF";
const ruleColor = "#C9C6D2";
const inputFill = "#FFF2CC";
const formulaFill = "#F4F3F7";
const summaryFill = "#E7F1F5";

sheet.getRange("A1").values = [["Forecast Accuracy Using the Arithmetic Mean"]];
sheet.getRange("A1").format.font = { name: fontFamily, size: 18, bold: true, color: titleColor };
sheet.getRange("A2").values = [["Forecasts use the arithmetic mean of all prior observed demand. Error is Dₜ − Fₜ."]];
sheet.mergeCells("A2:F2");
sheet.getRange("A2:F2").format.font = { name: fontFamily, size: 10, italic: true, color: "#595959" };
sheet.getRange("A2:F2").format.wrapText = true;

sheet.getRange("A4:F4").values = [["Period (t)", "Demand (Dₜ)", "Forecast (Fₜ)", "Error (eₜ)", "Absolute error |eₜ|", "Squared error eₜ²"]];
sheet.getRange("A4:F4").format = {
  fill: headerFill,
  font: { name: fontFamily, size: 11, bold: true, color: headerText },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  wrapText: true,
  borders: { preset: "outside", style: "thin", color: headerFill },
};

const demand = [9, 8, 9, 12, 9, 12, 11, 7, 13, 9, 11, 10];
sheet.getRange("A5:B16").values = demand.map((value, index) => [index + 1, value]);

sheet.getRange("C6").formulas = [["=AVERAGE($B$5:B5)"]];
sheet.getRange("C6:C16").fillDown();
sheet.getRange("D6").formulas = [["=B6-C6"]];
sheet.getRange("D6:D16").fillDown();
sheet.getRange("E6").formulas = [["=ABS(D6)"]];
sheet.getRange("E6:E16").fillDown();
sheet.getRange("F6").formulas = [["=D6^2"]];
sheet.getRange("F6:F16").fillDown();

sheet.getRange("A17").values = [["Sum"]];
sheet.getRange("B17").formulas = [["=SUM(B5:B16)"]];
sheet.getRange("C17").formulas = [["=SUM(C6:C16)"]];
sheet.getRange("D17").formulas = [["=SUM(D6:D16)"]];
sheet.getRange("E17").formulas = [["=SUM(E6:E16)"]];
sheet.getRange("F17").formulas = [["=SUM(F6:F16)"]];

sheet.getRange("A5:F17").format.font = { name: fontFamily, size: 11, color: "#222222" };
sheet.getRange("A5:A17").format.horizontalAlignment = "center";
sheet.getRange("B5:B16").format.fill = inputFill;
sheet.getRange("C5:F16").format.fill = formulaFill;
sheet.getRange("A5:F17").format.borders = {
  insideHorizontal: { style: "thin", color: ruleColor },
  bottom: { style: "thin", color: ruleColor },
};
sheet.getRange("A17:F17").format = {
  fill: "#DDD9E7",
  font: { name: fontFamily, size: 11, bold: true, color: "#222222" },
  borders: { top: { style: "medium", color: headerFill }, bottom: { style: "double", color: headerFill } },
};

sheet.getRange("A20:B20").values = [["Accuracy measure", "Value"]];
sheet.getRange("A20:B20").format = {
  fill: headerFill,
  font: { name: fontFamily, size: 11, bold: true, color: headerText },
  horizontalAlignment: "center",
};
sheet.getRange("A21:A23").values = [["MAD"], ["MSE"], ["Forecast periods"]];
sheet.getRange("B21").formulas = [["=AVERAGE(E6:E16)"]];
sheet.getRange("B22").formulas = [["=AVERAGE(F6:F16)"]];
sheet.getRange("B23").formulas = [["=COUNT(C6:C16)"]];
sheet.getRange("A21:B23").format = {
  fill: summaryFill,
  font: { name: fontFamily, size: 11, color: "#222222" },
  borders: { preset: "outside", style: "thin", color: "#A9BBC3" },
};
sheet.getRange("A21:A22").format.font.bold = true;

sheet.getRange("A26:F26").values = [["Source: user-provided screenshot, “Using Arithmetic Mean.”", null, null, null, null, null]];
sheet.getRange("A26:F26").format.font = { name: fontFamily, size: 9, italic: true, color: "#666666" };

sheet.getRange("A5:A17").format.numberFormat = "0";
sheet.getRange("B5:B17").format.numberFormat = "0.00";
sheet.getRange("C5:F17").format.numberFormat = "0.00";
sheet.getRange("B21:B22").format.numberFormat = "0.0000";
sheet.getRange("B23").format.numberFormat = "0";

sheet.getRange("A1:F26").format.verticalAlignment = "center";
sheet.getRange("A1:F26").format.rowHeight = 22;
sheet.getRange("A1").format.rowHeight = 30;
sheet.getRange("A2:F2").format.rowHeight = 24;
sheet.getRange("A4:F4").format.rowHeight = 34;

sheet.getRange("A:A").format.columnWidth = 16;
sheet.getRange("B:B").format.columnWidth = 16;
sheet.getRange("C:C").format.columnWidth = 17;
sheet.getRange("D:D").format.columnWidth = 15;
sheet.getRange("E:E").format.columnWidth = 22;
sheet.getRange("F:F").format.columnWidth = 22;

await fs.mkdir(outputDir, { recursive: true });

const tableCheck = await workbook.inspect({
  kind: "table",
  range: "Arithmetic Mean!A1:F23",
  include: "values,formulas",
  tableMaxRows: 30,
  tableMaxCols: 8,
});
console.log(tableCheck.ndjson);

const errorCheck = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
console.log(errorCheck.ndjson);

const preview = await workbook.render({
  sheetName: "Arithmetic Mean",
  range: "A1:F26",
  scale: 1.5,
  format: "png",
});
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

console.log(JSON.stringify({ outputPath, previewPath }));
