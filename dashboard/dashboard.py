import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

day_df=pd.read_csv("dashboard/day_df.csv")

# Mengurutkan bulan beradasrkan kategorikal
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
day_df['mnth'] = pd.Categorical(day_df['mnth'], categories=month_order, ordered=True)
season_order = ["Spring","Summer","Fall","Winter"]
day_df['season'] = pd.Categorical(day_df['season'], categories=season_order, ordered=True)
#dataframe yang akan diolah
def create_daily_rental(df):
    daily_rental = df.groupby(['dteday']).agg({"cnt":"sum"}).reset_index()
    return daily_rental
def create_season_data(df):
    season_data= df.groupby(['season'])['cnt'].sum().reset_index()
    return season_data
def create_monthly_data_df(df):
    monthly_data = df.groupby(['yr', 'mnth'])['cnt'].sum().reset_index()
    monthly_data = monthly_data.sort_values(['yr', 'mnth'], ascending=[True, True])
    return monthly_data
def create_data_2011(df):
    data_2011 = df[df['yr'] == 2011]
    return data_2011
def create_data_2012(df):
    data_2012 =df[df['yr'] == 2012]
    return data_2012
def create_corr_data(df):
    cor_data=df[['temp','atemp','hum','windspeed','cnt']]
    correlation_matrix = cor_data.corr()
    return cor_data
def create_customer_type(df):
    customer_type = df.agg({'casual': 'sum', 'registered': 'sum'})
    return customer_type
def create_day_type_data(df):
    day_type_data = df.groupby(['workingday'])[['casual', 'registered']].sum().reset_index()
    return day_type_data

day_df['dteday'] = pd.to_datetime(day_df['dteday'])
#mengatur filter tanggal dan waktu
min_date = day_df['dteday'].min().date()
max_date = day_df['dteday'].max().date()

with st.sidebar:
    st.image("index.jpg")    
    # Mengatur start date,end,date untuk digunakan pada filter tanggal
    start_date, end_date = st.date_input(
        label='Date for time range',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# convert dari timestamp ke datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Penerapan Filter Tanggal
main_df = day_df[(day_df['dteday'] >= start_date) & 
                 (day_df['dteday'] <= end_date)]
#Data perhitungan yang sudah menggunakan filter tanggal
filtered_counts = {
    'casual': main_df['casual'].sum(),
    'registered': main_df['registered'].sum()
}
daily_rental= create_daily_rental(main_df)
season_data = create_season_data(main_df)
monthly_data = create_monthly_data_df(main_df)
data_2011 = create_data_2011(main_df)
data_2012 = create_data_2012(main_df)
corr_data = create_corr_data(main_df)
customer_type = create_customer_type(main_df)
day_type_data = create_day_type_data(main_df)
st.title('🚲Icikiwir Rental Dashboard 🚲')
st.write('This Analysis using dataset from Kaggle "Bike Sharing Dataset"(https://www.kaggle.com/datasets/lakshmi25npathi/bike-sharing-dataset). The dataset is related to the two-year historical log corresponding to years 2011 and 2012 from Capital Bikeshare system, Washington D.C., USA')
st.write('For detailed Analysis and data processing step by step you can find it here : https://github.com/menggiGit33/Dashboard-Bike-Sharing-with-Streamlit/notebook.ipynb')
# Membuat jumlah penyewaan bulanan
st.header('Monthly Rentals')
col1, = st.columns(1)
with col1:
    total_Rental = daily_rental['cnt'].sum()
    st.metric('Total User Today :', value=total_Rental)

fig, ax = plt.subplots(figsize=(12,8))
sns.lineplot(data=monthly_data[monthly_data['yr'] == 2011], x='mnth', y='cnt', marker='o', label='2011', ax=ax, color='tab:blue')
sns.lineplot(data=monthly_data[monthly_data['yr'] == 2012], x='mnth', y='cnt', marker='X', label='2012', ax=ax, color='tab:red')
ax.tick_params(axis='x', labelsize=14)
ax.set_xticks(range(1, 13))
ax.grid(True,)
ax.legend()
st.pyplot(fig)

st.subheader('Insight:')
st.write('1. Customer tend to arise when February comes and the trends continues until it peaked in different month for 2011 in May and for 2012 peak was September and after reaching its peak the trends relatively decaying')        
st.write('2. As we can see 2012 was more profitable than 2011')        

#Membuat Barchart berdasarkan Musim
st.header('Seasonal Rental')
fig,ax= plt.subplots(figsize=(14,6))
sns.barplot(
    y='cnt', 
    x='season',
    data=season_data, 
    palette=sns.color_palette("pastel"))

ax.set_xlabel('Seasons')
ax.set_ylabel('Total Rent')
plt.gca().yaxis.get_major_formatter().set_scientific(False)
st.pyplot(fig)
st.subheader('Insight:')
st.write('1. Most preferably season to rent a bike was Fall and followed by Summer, then Winter and least preferably was Spring ')        
#Membuat PieChart Berdasarkan jenis pengguna
st.header ('Customer Type')
fig,ax=plt.subplots(figsize=(6,6))
labels = ['registered', 'casual']
values = customer_type[labels].values
def func(pct, allvalues):
    absolute = int(pct / 100. * sum(allvalues))  
    return f"{absolute} ({pct:.1f}%)"  

ax.pie(values, labels=labels, autopct=lambda pct: func(pct, values), colors=['#d47272', '#72BCD4'])
st.pyplot(fig)
st.subheader('Insight:')
st.write('1. There are 2 types of customer, there are Registered customer/member of bike rental subscriber and Casual/non-member. Registered member are majority of renter of this service and Casual was the minor ones')        

#Membuat Stacked BarChart berdasarkan Hari yang disenangi penyewa
st.header('Bike Rental Favorable Day')
col1,col2, = st.columns(2)
with col1:
    st.metric('Total Registered User Today :', value=filtered_counts['registered'])
with col2:
    st.metric('Total Casual User Today :', value=filtered_counts['casual'])
fig, ax = plt.subplots(figsize=(12, 6))

ax.bar(day_type_data['workingday'], day_type_data['casual'], label='Casual Users', color='#d47272')
ax.bar(day_type_data['workingday'], day_type_data['registered'], bottom=day_type_data['casual'], label='Registered Users', color='#72BCD4')

ax.set_xlabel('Day Type ')
ax.set_ylabel('Total Rentals')

ax.legend()
plt.gca().yaxis.get_major_formatter().set_scientific(False)
st.pyplot(fig)
st.subheader('Insight:')
st.write('1. with those 2 types of customer, our Members favored to use this service in Workingday same as non-member and they least favored in Non-Workingday  ')
