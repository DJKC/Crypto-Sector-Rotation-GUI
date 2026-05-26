# Crypto Sector Rotation Analyzer - GUI Version

## Graphical User Interface

A user-friendly GUI for analyzing cryptocurrency sector rotation without touching the command line. 

---

## Quick Start

### 1. Install Dependencies

```bash
# Navigate to the sector_rotation directory
cd /path/to/sector_rotation

# Install required packages (same as before)
pip install pandas numpy matplotlib seaborn scipy networkx

# Optional for interactive charts
pip install plotly
```

### 2. Launch the GUI

```bash
# From the sector_rotation directory
python gui_app.py

# Or use the launcher
python launch_gui.py
```

The GUI window will open immediately

---

## GUI Features

### **Auto-Scan for New Coins**

The GUI automatically detects new CSV files in your directory that aren't in the sector classification file.

**How it works:**
1. Select your CSV directory
2. Click "Scan Now" or enable "Auto-scan for new CSV files"
3. GUI shows you which symbols are new
4. Click "Yes" to open sector file and add them

**No manual file comparison needed**

### **Point-and-Click Configuration**

Replace command-line arguments with simple controls:

| Command Line | GUI Equivalent |
|--------------|----------------|
| `--csv-dir` | "Browse..." button → Select folder |
| `--timeframe 1d` | Dropdown: "1d" or "4h" |
| `--level subcategory` | Checkbox: Sub-Category |
| `--lookback 90` | Number spinner: 7-365 days |
| `--output` | "Browse..." → Select output folder |

### **Selective Visualization**

Choose which charts to generate:

- ☑ Sector Heatmap
- ☑ Cumulative Performance
- ☑ Rotation Network
- ☑ Lead-Lag Matrix
- ☐ Ranking Race *(slow, optional)*

Uncheck what you don't need to save time

### **Live Progress**

- **Real-time log** showing what's happening
- **Progress bar** during analysis
- **Stop button** to cancel long-running tasks

### **Multi-Level Analysis**

Analyze multiple hierarchy levels in one run:

- ☑ Category
- ☑ Sub-Category
- ☑ Segment

Check all three to analyze everything at once

---

## GUI Layout

```
┌─────────────────────────────────────────────────────────┐
│          Crypto Sector Rotation Analyzer                │
├─────────────────────────────────────────────────────────┤
│  Data Sources                                           │
│  CSV Directory:    [________________________] Browse    │
│  Sector File:      [________________________] Browse    │
│  Output Directory: [________________________] Browse    │
│  ☑ Auto-scan for new CSV files        [Scan Now]        │
├─────────────────────────────────────────────────────────┤
│  Analysis Parameters                                    │
│  Timeframe: [1d ▼]    Lookback Days: [90  ▼]            │
│  Analyze Levels:                                        │
│     ☐ Category  ☑ Sub-Category  ☐ Segment               │
├─────────────────────────────────────────────────────────┤
│  Visualizations to Generate                             │
│     ☑ Sector Heatmap        ☑ Cumulative Performance    │
│     ☑ Rotation Network      ☑ Lead-Lag Matrix           │
│     ☐ Ranking Race (slow)                               │
├─────────────────────────────────────────────────────────┤
│  [Run Analysis]  [Stop]  [Open Output]  [Clear Log]     │
│                                         [Progress Bar]  │
├─────────────────────────────────────────────────────────┤
│  Analysis Log                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ === STARTING ANALYSIS ===                         │  │
│  │ Loading CSV files...                              │  │
│  │ Found 244 coins                                   │  │
│  │ Analyzing Sub-Category...                         │  │
│  │ ✓ Analysis complete                               │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Auto-Scan Feature Details

### What It Does

Compares CSV files in your directory against symbols in your sector classification file.

**Example:**

Your directory has:
```
BTCUSDT_1d.csv
ETHUSDT_1d.csv
NEWCOINUSDT_1d.csv  ← Not in sector file
```

Your sector file has:
```
BTC,Settlement,Non-Programmable,Payment & Store of Value
ETH,Settlement,Programmable,General Purpose Smart Contract Platforms
(NEWCOIN missing)
```

**Auto-scan detects:** NEWCOIN is missing!

### How to Add New Coins

**Option 1: Let GUI Help**

1. Click "Scan Now"
2. GUI shows: "Found 1 new symbol: NEWCOIN"
3. Click "Yes" to open sector file
4. Add line: `NEWCOIN,Sectors,Finance,Trading`
5. Save and close
6. Run analysis → NEWCOIN included!

**Option 2: Manual**

1. Open `SYMBOLS_SECTORS_MERGED_Final.csv` in Excel/text editor
2. Add new row: `SYMBOL,Category,SubCategory,Segment`
3. Save
4. Scan will show all symbols are classified

### Supported Patterns

Auto-scan recognizes these filename formats:
- `SYMBOLUSDT_1d.csv` → Extracts "SYMBOL"
- `SYMBOLUSDT_4h.csv` → Extracts "SYMBOL"

**Examples:**
- `BTCUSDT_1d.csv` → BTC
- `ETHUSDT_4h.csv` → ETH
- `AAVEUSDT_1d.csv` → AAVE

---

## Workflow Examples

### Workflow 1: Quick Daily Check

1. **Launch GUI**
2. **Scan** for new coins (if any)
3. **Select:**
   - Timeframe: 1d
   - Level: Sub-Category
   - Lookback: 30 days
   - Heatmap + Cumulative only
4. **Run Analysis** (takes ~30 seconds)
5. **Open Output** folder
6. **View charts** in browser

**Total time: 2 minutes**

### Workflow 2: Deep Weekly Analysis

1. **Launch GUI**
2. **Select:**
   - Timeframe: 1d
   - Levels: ALL (Category, Sub-Category, Segment)
   - Lookback: 90 days
   - ALL visualizations
3. **Run Analysis** (takes ~5 minutes)
4. **Review logs** for rotation patterns
5. **Open charts** in browser
6. **Compare levels** for insights

**Total time: 10 minutes**

### Workflow 3: Intraday Rotation

1. **Launch GUI**
2. **Select:**
   - Timeframe: 4h
   - Level: Sub-Category
   - Lookback: 14 days
   - Network + Lead-Lag only
3. **Run Analysis**
4. **View rotation flows**

**Use case:** Catch sector rotations happening today/this week

### Workflow 4: Adding 50 New Coins

1. **Download 50 new CSV files** → Place in your CSV directory
2. **Launch GUI** → Click "Scan Now"
3. **GUI shows:** "Found 50 new symbols"
4. **Click Yes** → Sector file opens
5. **Add 50 lines** to sector file (copy/paste from spreadsheet)
6. **Save and close**
7. **Scan again** → "All symbols classified"
8. **Run Analysis** → All 295 coins included!

**No code changes, no manual file comparison!**

---

## Configuration Tips

### For Fast Analysis

- Use **1 hierarchy level** (Sub-Category)
- Use **30-day lookback**
- Generate **2-3 visualizations** only
- Skip "Ranking Race" (it's slow)

**Analysis time: ~30 seconds**

### For Comprehensive Analysis

- Use **ALL hierarchy levels**
- Use **90-180 day lookback**
- Generate **ALL visualizations**
- Include "Ranking Race"

**Analysis time: ~5-10 minutes**

### For Custom Research

Mix and match:
- Short lookback (7 days) for recent rotations
- Long lookback (180 days) for cycle analysis
- Segment level for granular detail
- Category level for big picture

---

## Troubleshooting

### GUI Won't Launch

**Problem:** Double-clicking doesn't work  
**Solution:** Open terminal and run:
```bash
cd /path/to/sector_rotation
python gui_app.py
```

### "Module not found" Error

**Problem:** Can't find sector_rotation modules  
**Solution:** Make sure GUI file is in same directory as sector_rotation modules:
```
your_folder/
  ├── gui_app.py          ← GUI application
  ├── launch_gui.py       ← Launcher
  ├── data_loader.py      ← Module
  ├── sector_aggregator.py
  ├── rotation_analyzer.py
  └── visualizer.py
```

### Scan Finds Nothing

**Problem:** "All symbols classified" but you know there are new ones  
**Solution:** 
- Check filename format: Must be `SYMBOLUSDT_1d.csv`
- Check timeframe dropdown: Must match CSV files (1d vs 4h)
- Verify CSV directory path is correct

### Analysis Takes Forever

**Problem:** Been running for 10+ minutes  
**Solutions:**
- Click "Stop" button
- Reduce lookback days (try 30 instead of 180)
- Uncheck "Ranking Race" visualization
- Analyze one level at a time instead of all three

### Visualizations Look Wrong

**Problem:** Charts show strange patterns  
**Check:**
- Lookback period (too short = noisy)
- Data quality (missing dates in CSVs?)
- Timeframe selection (4h vs 1d)

### Output Folder Empty

**Problem:** Analysis completes but no files  
**Solution:**
- Check log for errors
- Verify output directory has write permissions
- Try different output directory (Desktop, Documents, etc.)

---

## Best Practices

### Data Management

1. **Keep CSVs organized** in one dedicated folder
2. **Name CSVs consistently**: `SYMBOLUSDT_1d.csv`
3. **Update sector file regularly** when adding coins
4. **Backup sector file** before making changes
5. **Use version control** for sector file (git)

### Analysis Workflow

1. **Scan first** every time you launch GUI
2. **Start with Sub-Category** level (best balance)
3. **Use shorter lookback** for testing
4. **Enable all visualizations** only for final analysis
5. **Compare timeframes** (1d vs 4h) for confirmation

### Performance Optimization

1. **Close other programs** during analysis
2. **Use SSD** for CSV storage (faster loading)
3. **Analyze one level** at a time for speed
4. **Skip visualizations** you don't need
5. **Use 30-60 day lookback** for routine analysis

---

## Understanding the Output

After clicking "Run Analysis", you'll see console output AND get visualization files.

### Console Output Structure

```
=== STARTING ANALYSIS ===
Loading CSV files from /path/to/csvs...
Found 244 files
Successfully loaded 244 coins

=== ANALYZING: SUBCATEGORY ===

🔥 TOP 5 PERFORMERS:
  Finance    | Return: +12.34%
  Gaming     | Return:  +8.92%
  ...

💰 CAPITAL ROTATION FLOWS:
  DeFi → Gaming (flow: 234.5)
  ...

🔮 LEAD-LAG RELATIONSHIPS:
  Finance leads Gaming by 3 days
  ...

Generating visualizations...
  - Creating heatmap... ✓
  - Creating network... ✓

ANALYSIS COMPLETE!
```

### Output Files Generated

In your output directory:

```
sector_rotation_output/
├── heatmap_subcategory_1d.html      ← Open in browser
├── cumulative_subcategory_1d.html   ← Open in browser
├── network_subcategory_1d.html      ← Open in browser
├── leadlag_subcategory_1d.png       ← Open in image viewer
└── race_subcategory_1d.html         ← Open in browser (if enabled)
```

**Click "Open Output Folder" button** → Files appear → Double-click to view!

---

## Advanced Features

### Batch Processing

Want to analyze multiple timeframes?

1. Run analysis with `1d` timeframe → saves to output folder
2. Change timeframe dropdown to `4h`
3. Run analysis again → saves with different filename
4. Compare results side-by-side!

### Custom Output Locations

Organize by date:
```
Output Directory: ~/sector_analysis/2024-12-09/
```

Organize by timeframe:
```
Output Directory: ~/sector_analysis/daily/
Output Directory: ~/sector_analysis/4hour/
```

### Multi-Monitor Setup

1. **Monitor 1:** GUI application (run analysis)
2. **Monitor 2:** Browser with charts (view results)
3. **Monitor 3:** Sector file + spreadsheet (data management)

Perfect for live analysis!

---

## FAQ

**Q: Can I run multiple analyses simultaneously?**  
A: No, run one at a time. The "Stop" button cancels current analysis.

**Q: Does auto-scan modify my files?**  
A: No! It only READS files and SHOWS you what's new. You manually decide whether to add symbols.

**Q: What if I close GUI during analysis?**  
A: Analysis stops immediately. Partial results may be saved to output folder.

**Q: Can I use this without the command line?**  
A: Yes! GUI is 100% self-contained. Never touch terminal if you don't want to.

**Q: How do I update the software?**  
A: Replace the Python files with new versions. Your data files aren't touched.

**Q: Can I customize the GUI?**  
A: Yes! It's Python code. Edit `gui_app.py` to change layout, add features, etc.

---

## Learn More

- **CLI Version:** See `dashboard.py` for command-line usage
- **Module Documentation:** Each `.py` file has detailed comments
- **Customization:** See `EXTENSIBILITY_GUIDE.md`
- **Full Manual:** See `README.md`

---

## Keyboard Shortcuts

The GUI supports standard shortcuts:

- **Ctrl+A** (Cmd+A on Mac) - Select all in log
- **Ctrl+C** - Copy from log
- **Ctrl+V** - Paste in path fields

---

## Summary

**The GUI makes everything easier:**

No command-line typing  
Point-and-click configuration  
Auto-detects new coins  
Live progress updates  
One-click output access  
Selective visualization generation  
Multi-level analysis in one run  
Professional and intuitive  

**Same powerful analysis, zero complexity!**

---

## Getting Help

If you encounter issues:

1. Check the **Analysis Log** in GUI for error messages
2. Read the **Troubleshooting** section above
3. Verify your file paths and formats
4. Try with a smaller dataset first (10-20 coins)

The GUI shows you exactly what's happening at each step!

---

**Enjoy my graphical sector rotation analyzer!!!!!*

<img width="224" height="205" alt="screenshot_options" src="https://github.com/user-attachments/assets/5bc19b5c-a92f-4c54-a8f7-e578ec384d32" />

<img width="351" height="134" alt="screenshot" src="https://github.com/user-attachments/assets/6aa5751d-5dce-4149-9acf-e5cf332eefd8" />
