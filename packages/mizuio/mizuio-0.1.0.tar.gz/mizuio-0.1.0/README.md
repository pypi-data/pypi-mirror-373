
# mizuio - Python Data Processing Toolkit

mizuio is a comprehensive Python toolkit for data cleaning, visualization, and analysis. It provides a modern command-line interface and Python API for efficient data workflows, leveraging Pandas, NumPy, Matplotlib, Seaborn, and scikit-learn.

---

## 🚀 Features

### Data Cleaning (`DataCleaner`)
- Handle missing values: drop, fill, or interpolate
- Remove duplicates by columns
- Automatic data type conversion
- Outlier detection and removal (IQR, Z-score)
- Text normalization (case, whitespace)

### Data Visualization (`DataVisualizer`)
- Histograms and distribution plots
- Box plots for outlier analysis
- Scatter plots for variable relationships
- Correlation heatmaps
- Bar and line charts (categorical/time series)
- Missing value visualization

### Utility Tools (`DataUtils`)
- Multi-format support: CSV, JSON, Excel, Parquet, Pickle
- Data validation (columns, types, value ranges)
- Data sampling (random, systematic, stratified)
- Data splitting (train/validation/test)
- Categorical encoding (label, one-hot, ordinal)
- Feature scaling (standard, minmax, robust)

---

## 📦 Installation

### Requirements
- Python 3.7+
- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn

### Steps
1. **Clone the repository:**
	```sh
		git clone https://github.com/mertskzc/mizuio.git
		cd mizuio
	```
2. **Install dependencies:**
	```sh
	pip install -r requirements.txt
	```
3. **Install in development mode (optional):**
	```sh
	pip install -e .
	```

---

## 🖥️ Usage

### Command Line Interface

mizuio provides a CLI for common data tasks:

```sh
# Clean a dataset
mizuio clean data.csv --output cleaned_data.csv --remove-duplicates --fill-missing --remove-outliers

# Visualize a column
mizuio visualize data.csv --plot histogram --column age --output age_hist.png

# Show data info
mizuio info data.csv
```

#### CLI Commands
- `clean`: Clean data (remove duplicates, fill missing, remove outliers)
- `visualize`: Visualize data (histogram, boxplot, scatter, correlation)
- `info`: Show data summary (shape, memory, columns, missing values, duplicates)

---

## 🧪 Testing

Run all tests:
```sh
python -m pytest tests/
```
Run a specific test file:
```sh
python -m pytest tests/test_cleaner.py
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add feature'`)
4. Push your branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 📞 Contact

- **Project Link:** [https://github.com/mertskzc/mizuio](https://github.com/mertskzc/mizuio)
- **E-mail:** mertskzc@gmail.com

---

## 🙏 Acknowledgements

mizuio uses the following open source libraries:
- [pandas](https://pandas.pydata.org/)
- [numpy](https://numpy.org/)
- [matplotlib](https://matplotlib.org/)
- [seaborn](https://seaborn.pydata.org/)
- [scikit-learn](https://scikit-learn.org/)