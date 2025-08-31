# Ravenclaw - Intelligent Data Preprocessing and Clustering

A comprehensive toolkit for automated feature engineering and clustering with pandas DataFrames. Ravenclaw intelligently detects column types, converts temporal strings, creates cyclical encodings, and performs automatic clustering - all with minimal configuration.

## 🎯 Key Features

### **Intelligent Preprocessing Pipeline**
- **Automatic Detection**: Identifies datetime, date, time, and categorical columns in string format
- **Smart Conversion**: Converts string temporal data to proper types with format learning
- **Cyclical Encoding**: Creates sin/cos features for temporal data (perfect for ML models)
- **One-Hot Encoding**: Handles categorical variables with temporal safety checks
- **Sklearn Compatible**: Standard fit/transform interface for seamless integration

### **Advanced Clustering**
- **AutoKMeans**: Automatically determines optimal number of clusters
- **Multiple Methods**: Silhouette, Calinski-Harabasz, Davies-Bouldin, and Elbow methods
- **Built-in Preprocessing**: Integrated scaling and imputation
- **Column Selection**: Flexible include/exclude functionality
- **Sklearn Interface**: Drop-in replacement for standard KMeans

## 🚀 Quick Start

### Installation

```bash
pip install ravenclaw
```

### Complete ML Pipeline Example

Here's how to preprocess mixed data and cluster it in a single pipeline:

```python
import pandas as pd
import numpy as np
from ravenclaw.preprocessing.df_encoders import FeatureEngineeringPipeline
from ravenclaw.clustering.kmeans import AutoKMeans
from sklearn.pipeline import Pipeline

# Create sample mixed data (the kind you get in real life!)
np.random.seed(42)
df = pd.DataFrame({
    'timestamp': ['2023-01-15 14:30:00', '2023-06-30 09:15:00', '2023-12-25 18:45:00'] * 50,
    'date_created': ['2023-01-15', '2023-06-30', '2023-12-25'] * 50,
    'time_of_day': ['14:30:00', '09:15:00', '18:45:00'] * 50,
    'category': ['Premium', 'Standard', 'Basic'] * 50,
    'region': ['North', 'South', 'East', 'West'] * 37 + ['North', 'South', 'East'],
    'revenue': np.random.normal(1000, 200, 150),
    'customer_age': np.random.randint(18, 80, 150),
    'satisfaction': np.random.uniform(1, 5, 150)
})

# Add some missing values (real data is messy!)
df.loc[np.random.choice(150, 10), 'revenue'] = np.nan
df.loc[np.random.choice(150, 5), 'satisfaction'] = np.nan

print(f"Original data: {df.shape[1]} columns")
print(f"Column types: {df.dtypes.value_counts().to_dict()}")

# Step 1: Feature Engineering Pipeline
# Automatically detects and converts temporal strings, creates cyclical features
preprocessor = FeatureEngineeringPipeline.create_default()
processed_df = preprocessor.fit_transform(df)

print(f"After preprocessing: {processed_df.shape[1]} columns")
print(f"New features: {list(processed_df.columns)}")

# Step 2: Automatic Clustering with Built-in Imputation
# AutoKMeans handles missing values and scaling automatically
clusterer = AutoKMeans(
    max_k=8,                           # Try up to 8 clusters
    method='silhouette',               # Use silhouette score for k-selection
    scale=True,                        # Scale features (important for clustering)
    impute=True,                       # Handle missing values
    impute_strategy='median',          # Use median for imputation
    ignore_non_numeric=True,           # Silently skip non-numeric columns
    random_state=42
)

# Fit and predict clusters
cluster_labels = clusterer.fit_predict(processed_df)

print(f"Optimal clusters found: {clusterer.n_clusters_}")
print(f"Cluster distribution: {np.bincount(cluster_labels)}")

# Add clusters back to original data for analysis
df['cluster'] = cluster_labels
print("\nCluster summary:")
print(df.groupby('cluster')[['revenue', 'customer_age', 'satisfaction']].mean())
```

### Sklearn Pipeline Integration

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Create a complete sklearn pipeline
ml_pipeline = Pipeline([
    ('preprocessing', FeatureEngineeringPipeline.create_default()),
    ('clustering', AutoKMeans(max_k=5, scale=True, impute=True))
])

# One-line fit and predict
cluster_labels = ml_pipeline.fit_predict(df)
```

## 🔧 Advanced Usage

### Custom Preprocessing Pipeline

```python
from ravenclaw.preprocessing.df_encoders import (
    StringTemporalConverter,
    DateTimeConverter, 
    DayOfYearEncoder,
    HourOfDayEncoder,
    OneHotEncoder,
    FeatureEngineeringPipeline
)

# Build custom pipeline with specific encoders
custom_pipeline = FeatureEngineeringPipeline([
    StringTemporalConverter(),          # String temporal → proper types
    DateTimeConverter(),                # datetime → day_of_year + hour_of_day
    DayOfYearEncoder(),                 # day_of_year → sin/cos features
    HourOfDayEncoder(),                 # hour_of_day → sin/cos features
    OneHotEncoder(exclude_columns=['timestamp'])  # Categorical → binary (skip temporal)
])

result = custom_pipeline.fit_transform(df)
```

### Clustering with Column Selection

```python
# Cluster only specific columns
clusterer = AutoKMeans(
    include_columns=['revenue', 'customer_age', 'satisfaction'],
    max_k=6,
    method='calinski_harabasz',
    impute=True,
    impute_strategy='mean'
)

labels = clusterer.fit_predict(df)

# Get clustering diagnostics
diagnostics = clusterer.get_diagnostics()
print(f"Tried k values: {diagnostics['candidate_ks']}")
print(f"Scores: {diagnostics['scores']}")
```

### Individual Encoder Usage

```python
from ravenclaw.preprocessing.df_encoders import StringTemporalConverter

# Just convert temporal strings
converter = StringTemporalConverter()
converter.fit(df)

# See what formats were learned
formats = converter.get_learned_formats()
print("Detected formats:", formats)

# Transform the data
converted_df = converter.transform(df)
```

## 🧠 How It Works

### Intelligent Column Detection
Ravenclaw uses priority-based classification to handle ambiguous cases:
```
datetime > date > time > day_of_week > day_of_year > hour_of_day > categorical
```

### Automatic K-Selection Methods
- **Silhouette Score**: Measures cluster cohesion and separation
- **Calinski-Harabasz**: Ratio of between-cluster to within-cluster variance
- **Davies-Bouldin**: Average similarity between clusters
- **Elbow Method**: Finds the "elbow" in the inertia curve

### Built-in Imputation
AutoKMeans includes sklearn's SimpleImputer with strategies:
- `'mean'`: Replace with column mean (numeric only)
- `'median'`: Replace with column median (numeric only)  
- `'most_frequent'`: Replace with mode (works for all types)
- `'constant'`: Replace with a constant value

## 📊 What You Get

### Before Ravenclaw
```python
# Manual feature engineering pain
df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
df['day_of_year'] = pd.to_datetime(df['timestamp']).dt.dayofyear
df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
# ... repeat for every temporal column
# ... handle missing values
# ... scale features
# ... try different k values
# ... compare clustering metrics
```

### After Ravenclaw
```python
# One-liner magic ✨
pipeline = FeatureEngineeringPipeline.create_default()
processed_df = pipeline.fit_transform(df)
labels = AutoKMeans(max_k=8).fit_predict(processed_df)
```

## 🛠️ Development

```bash
# Clone and setup
git clone https://github.com/idin/ravenclaw.git
cd ravenclaw

# Create conda environment  
conda env create -f environment.yml
conda activate ravenclaw

# Install in development mode
pip install -e .

# Run tests (244 tests, all passing!)
pytest tests/
```

## 📈 Project Status

- ✅ **244 Tests Passing** - Comprehensive test coverage
- ✅ **Production Ready** - Used in real ML workflows
- ✅ **Zero Warnings** - Clean, maintainable codebase
- ✅ **Sklearn Compatible** - Drop-in replacement for standard tools
- ✅ **Type Safe** - Full type hints and error handling

## 🎯 Perfect For

- **Data Scientists**: Spend less time on preprocessing, more on insights
- **ML Engineers**: Robust, tested pipelines for production
- **Analysts**: Intelligent automation for common data tasks
- **Anyone**: Who works with messy, real-world pandas DataFrames

## 📄 License

MIT License - Use it, love it, contribute to it!

---

*Ravenclaw: Because your data deserves intelligent preprocessing* 🧙‍♂️✨