import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


st.set_page_config(page_title="Churn Dashboard", layout="wide")

def load_data():
    df = pd.read_csv("WA_Fn-UseC_-Telco-Customer-Churn.csv")
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    df['TotalCharges'].fillna(df['TotalCharges'].median(), inplace=True)
    return df

df = load_data()

st.sidebar.header("Filters")

contract = st.sidebar.multiselect(
    "Contract Type",
    df['Contract'].unique(),
    default=df['Contract'].unique()
)

internet = st.sidebar.multiselect(
    "Internet Service",
    df['InternetService'].unique(),
    default=df['InternetService'].unique()
)

tenure_range = st.sidebar.slider(
    "Tenure (Months)",
    df['tenure'].min(),
    df['tenure'].max(),
    (0,72)
)

filtered_df = df[
    (df['Contract'].isin(contract)) &
    (df['InternetService'].isin(internet)) &
    (df['tenure'].between(*tenure_range))
]

st.title("Churn Analysis Dashboard")

total_customers = len(filtered_df)
churn_rate = (filtered_df['Churn'] == 'Yes').mean() * 100
avg_monthly = filtered_df['MonthlyCharges'].mean()
avg_tenure = filtered_df['tenure'].mean()

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Customers", f"{total_customers:,}")
k2.metric("Churn Rate", f"{churn_rate:.2f}%")
k3.metric("Average Monthly Charges", f"₹{avg_monthly:.2f}")
k4.metric("Average Tenure", f"{avg_tenure:.1f} months")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Churn Distribution")
    churn_counts = filtered_df['Churn'].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(y=churn_counts.index, x=churn_counts.values, ax=ax)
    ax.set_xlabel("Customers")
    st.pyplot(fig)

with col2:
    st.subheader("Churn by Contract Type")
    churn_contract = pd.crosstab(
        filtered_df['Contract'],
        filtered_df['Churn'],
        normalize='index'
    )*100

    fig, ax = plt.subplots()
    churn_contract.plot(kind='bar', stacked=True, ax=ax)
    ax.set_ylabel("Percentage")
    st.pyplot(fig)

st.subheader("Average Numerical Features by Churn")

filtered_df['Churn_num'] = (filtered_df['Churn'] == 'Yes').astype(int)

num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']

mean_by_churn = (
    filtered_df
    .groupby('Churn_num')[num_cols]
    .mean()
    .T
)

mean_by_churn.columns = ['No Churn', 'Churn']
mean_by_churn['Diff'] = abs(mean_by_churn['Churn'] - mean_by_churn['No Churn'])

mean_by_churn_sorted = mean_by_churn.sort_values('Diff', ascending=False)

fig, ax = plt.subplots(figsize=(15,8))
mean_by_churn_sorted.drop(columns='Diff').plot(kind='bar', ax=ax)
ax.set_ylabel("Mean")
ax.set_title("Sorted Feature Impact on Churn")
st.pyplot(fig)


st.subheader("Filtered Data Preview")
st.dataframe(filtered_df.head(20))
