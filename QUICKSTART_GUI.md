# GUI Quick Start - 3 Steps - Lets go!!!!!!!!!!!!!!!!!

## Step 1: Launch the GUI

```bash
cd /path/to/sector_rotation_gui
python gui_app.py
```

**Or** double-click `launch_gui.py` (if Python is set as default)

---

## Step 2: Configure Paths

In the GUI window:

1. **CSV Directory**: Click "Browse" → Select your folder with `*USDT_1d.csv` files
   - Example: `/Users/human/Documents/Coding/Python//Crypto/Kraken/data/price_symbol_data/binance_1d_csv`

2. **Sector File**: Click "Browse" → Select your `SYMBOLS_SECTORS_MERGED_Final.csv`

3. **Output Directory**: Leave default or click "Browse" to choose where results go

4. Check "Auto-scan for new CSV files"

5. Click **"Scan Now"** → GUI shows if any new coins need classification

---

## Step 3: Run Analysis

### Basic Configuration:

- **Timeframe**: `1d` (dropdown)
- **Lookback Days**: `60` (spinner)
- **Analyze Levels**: ☑ Sub-Category
- **Visualizations**: ☑ Heatmap, ☑ Cumulative, ☑ Network

Click **"Run Analysis"**

**Wait 1-2 minutes** → Watch log for progress

When done: Click **"Open Output Folder"** → View your charts!

---

## That's It!

Three steps:
1. Launch GUI
2. Set paths
3. Click run

**No command line needed.**  
**No manual file scanning.**  
**No complex configuration.**

---

## Next Steps

- **Add more visualizations**: Check the Lead-Lag Matrix box
- **Try different timeframes**: Switch to `4h` (if you have 4h CSVs)
- **Analyze all levels**: Check Category, Sub-Category, AND Segment
- **Adjust lookback**: Try 30 days (faster) or 180 days (comprehensive)

Read `GUI_README.md` for full details!

---

## Pro Tips

1. **First time?** Start with 30-day lookback to see how fast it runs
2. **Adding coins?** Click "Scan Now" after copying new CSVs
3. **Want speed?** Uncheck "Ranking Race" (it's slow)
4. **Lost output?** Look in your home directory → `sector_rotation_output/`
5. **Errors?** Read the Analysis Log at bottom of GUI window

---

**Happy analyzing**
