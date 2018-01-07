# Graphing
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import StringIO
import base64

def display_fb_shares(target):
    img = StringIO.StringIO()

    df = pd.read_csv("./app/resources/details.csv")
    bins = [0, 500000 , 1000000, 5000000, 10000000, 50000000, 100000000, 500000000, 1000000000, 5000000000]
    groups = df.groupby(pd.cut(df.collected_amt, bins))
    df_binned = pd.DataFrame(groups.mean().fb_share_count)
    df_binned = df_binned.reset_index()

    columns = ['0 - Rp500.000,-', 
       '> Rp500.000, - Rp1.000.000,-', 
       '>Rp1.000.000,- - Rp5.000.000,-',
       '>Rp5.000.000,- - Rp10.000.000,-',
       '>Rp10.000.000,- - Rp50.000.000,-',
       '>Rp50.000.000,- - Rp100.000.000,-',
       '>Rp100.000.000,- - Rp500.000.000,-',
       '>Rp500.000.000,- - Rp1.000.000.000,-',
       '>Rp1.000.000.000,- - Rp5.000.000.000,-']

    colors = ["#999999"]*len(bins)
    # Set stand out color
    for i in range(0, len(columns)):
        try:
            if target in list(df_binned['collected_amt'])[i]:
                colors[i] = "#2ecc71"
                target_bin = columns[i]
                target_bin_avg = int(df_binned['fb_share_count'][i])
                break
                
        except:
            if str(target) in list(df_binned['collected_amt'])[i]:
                colors[i] = "#2ecc71"
                target_bin = columns[i]
                target_bin_avg = int(df_binned['fb_share_count'][i])
                break

    fig, ax = plt.subplots(figsize=(8,4))
    ax = sns.barplot(x='collected_amt', y='fb_share_count', data=df_binned, palette=colors)
    ax.set(xlabel='Collected Amount', ylabel='Average Facebook Shares')
    ax.set_xticklabels(columns,rotation=30)
    plt.tight_layout()

    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue())
    
    return {'target_bin': target_bin, 'target_bin_avg': target_bin_avg, 'plot_url': plot_url}