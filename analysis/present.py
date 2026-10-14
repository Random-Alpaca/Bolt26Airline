"""Create standalone plots, a chart PDF, and a browsable analysis workbook.

Requires matplotlib and openpyxl; analytical tables themselves use the stdlib.
"""
import csv
import json
import re
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_pdf import PdfPages
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule

HERE=Path(__file__).resolve().parent
TABLES=HERE/'tables'
CHARTS=HERE/'charts'
CHARTS.mkdir(exist_ok=True)
BLUE='#235789'; TEAL='#159895'; RED='#c44b4f'; GOLD='#dc9a35'; GREY='#607080'
P1='Sep 2024–Aug 2025'; P2='Sep 2025–Aug 2026'


def read(name):
    with (TABLES/name).open(newline='') as f:return list(csv.DictReader(f))


def number(row,col):return float(row[col])


def style():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
      'axes.spines.right':False,'axes.titleweight':'bold','axes.labelcolor':'#24334a',
      'text.color':'#24334a','axes.edgecolor':'#b8c5d0','savefig.facecolor':'white',
      'figure.facecolor':'white','axes.grid':False})


def finish(fig,name,pdf,note):
    fig.text(.02,.018,note,fontsize=8,color=GREY,va='bottom',wrap=True)
    fig.subplots_adjust(bottom=.15,top=.90,left=.10,right=.96,hspace=.40,wspace=.30)
    fig.savefig(CHARTS/(name+'.png'),dpi=180)
    fig.savefig(CHARTS/(name+'.svg'))
    pdf.savefig(fig)
    plt.close(fig)


def draw_charts():
    style()
    net=read('network_period.csv'); monthly=read('network_monthly.csv')
    route=[r for r in read('routes_period.csv') if r['period']=='2']
    common='Deduplicated transactions; unspecified source currency. Contribution excludes gates and other unobserved costs.'
    with PdfPages(HERE/'analysis_charts.pdf') as pdf:
        fig,axs=plt.subplots(1,3,figsize=(13,5))
        for ax,key,title in zip(axs,['net_revenue','recorded_cost','contribution_before_gates'],['Net recorded revenue','Recorded operating costs','Contribution before gates']):
            vals=[number(r,key)/1e6 for r in net]
            bars=ax.bar(['Period 1','Period 2'],vals,color=[BLUE,TEAL] if key!='contribution_before_gates' else [GOLD,RED],width=.55)
            ax.bar_label(bars,labels=[f'${v:,.2f}M' for v in vals],padding=4,fontsize=11)
            ax.set_title(title,fontsize=12);ax.set_ylabel('Millions');ax.margins(y=.25);ax.axhline(0,color=GREY,linewidth=.6)
        fig.suptitle('Activity growth outpaced recorded revenue',fontsize=18)
        finish(fig,'01_period_comparison',pdf,f'Period 1: {P1}. Period 2: {P2}.\n'+common)

        fig,(ax,bx)=plt.subplots(2,1,figsize=(13,7),sharex=True,gridspec_kw={'height_ratios':[2,1]})
        x=list(range(24)); labels=[r['month'] for r in monthly]
        ax.plot(x,[number(r,'revenue')/1e6 for r in monthly],label='Net recorded revenue',color=TEAL,marker='o')
        ax.plot(x,[number(r,'cost')/1e6 for r in monthly],label='Recorded cost',color=RED,marker='o')
        ax.set_ylabel('Millions');ax.legend(frameon=False,ncol=2);ax.set_title('Every month from March 2025 onward had negative contribution')
        vals=[number(r,'contribution')/1e6 for r in monthly]
        bx.bar(x,vals,color=[TEAL if v>=0 else RED for v in vals]);bx.axhline(0,color=GREY,lw=.8)
        bx.set_ylabel('Contribution, M');bx.set_xticks(x[::2],labels[::2],rotation=35,ha='right')
        for a in (ax,bx):a.axvline(11.5,color=GREY,linestyle='--',alpha=.6)
        finish(fig,'02_monthly_trend',pdf,'Dashed line separates the two complete comparison periods. Two years do not establish recurring seasonality.\n'+common)

        metrics=json.loads((HERE/'network_metrics.json').read_text());a=metrics['1'];b=metrics['2']
        costperiod=read('costs_period.csv')
        start=a['contribution']/1e8
        changes=[(b['revenue']-a['revenue'])/1e8]+[-(number(costperiod[1],c)-number(costperiod[0],c))/1e6 for c in ['fuel_cost','crew_cost','maintenance_cost','food_cost']]
        names=['Period 1','Revenue','Fuel','Crew','Maintenance','Food','Period 2']
        fig,ax=plt.subplots(figsize=(12,6));running=start
        ax.bar(0,start,color=BLUE)
        ax.text(0,start-.9,f'{start:,.2f}',ha='center',va='top')
        for i,v in enumerate(changes,1):
            ax.bar(i,abs(v),bottom=min(running,running+v),color=TEAL if v>0 else RED)
            ax.text(i,max(running,running+v)+.8,f'{v:+,.2f}',ha='center',fontsize=10)
            ax.plot([i-1+.4,i-.4],[running,running],color=GREY,lw=.8)
            running+=v
        ax.bar(6,running,color=BLUE);ax.text(6,running-1,f'{running:,.2f}',ha='center',va='top')
        ax.set_xticks(range(7),names);ax.axhline(0,color=GREY,lw=.8);ax.set_ylabel('Millions');ax.set_ylim(running-9,5)
        ax.set_title('The $36.02M deterioration is driven by a $45.39M cost increase',fontsize=15)
        finish(fig,'03_contribution_bridge',pdf,common)

        ranked=sorted(route,key=lambda r:number(r,'contribution_before_gates'))
        shown=ranked[:10]+ranked[-6:]
        fig,ax=plt.subplots(figsize=(12,8));vals=[number(r,'contribution_before_gates')/1e6 for r in shown]
        bars=ax.barh(range(len(shown)),vals,color=[TEAL if v>=0 else RED for v in vals]);ax.set_yticks(range(len(shown)),[r['route'] for r in shown])
        ax.invert_yaxis();ax.axvline(0,color=GREY,lw=.8);ax.bar_label(bars,labels=[f'{v:,.2f}' for v in vals],padding=4,fontsize=9)
        ax.set_xlim(-12,3);ax.set_xlabel('Contribution before gates, millions')
        ax.set_title('Montréal–Vancouver dominates the latest period’s losses',fontsize=15)
        finish(fig,'04_route_contribution',pdf,'Period 2: ten lowest and six highest directional contributions. Route codes are directional.\n'+common)

        fig,ax=plt.subplots(figsize=(10,7))
        for r in route:
            x=number(r,'revenue')/1e6;y=number(r,'cost')/1e6
            ax.scatter(x,y,s=number(r,'cost_event_count')*.17,color=RED if y>x else TEAL,alpha=.75,edgecolor='white',lw=.5)
        for r in sorted(route,key=lambda r:abs(number(r,'contribution_before_gates')),reverse=True)[:6]:
            ax.annotate(r['route'],(number(r,'revenue')/1e6,number(r,'cost')/1e6),xytext=(5,5),textcoords='offset points',fontsize=9)
        maximum=max(max(number(r,'revenue'),number(r,'cost')) for r in route)/1e6*1.08
        ax.plot([0,maximum],[0,maximum],'--',color=GREY,label='Recorded break-even')
        ax.set_xlim(0,maximum);ax.set_ylim(0,maximum);ax.set_xlabel('Net recorded revenue, millions');ax.set_ylabel('Recorded operating cost, millions')
        ax.legend(frameon=False);ax.set_title('28 of 54 directions cost more than their recorded revenue')
        finish(fig,'05_route_revenue_cost',pdf,'Period 2. Bubble size reflects cost events, a proxy for activity; no passenger or flight IDs are supplied.\n'+common)

        allmonths=sorted({r['month'] for r in monthly}); codes=[r['route'] for r in ranked]
        cells={(r['route'],r['month']):number(r,'contribution_before_gates')/1000 for r in read('routes_monthly.csv')}
        import numpy as np
        matrix=np.array([[cells.get((r,m),np.nan) for m in allmonths] for r in codes])
        fig,ax=plt.subplots(figsize=(13,14));limit=float(np.nanmax(np.abs(matrix)))
        im=ax.imshow(matrix,cmap='RdYlGn',vmin=-limit,vmax=limit,aspect='auto')
        ax.set_yticks(range(len(codes)),codes,fontsize=8);ax.set_xticks(range(24),allmonths,rotation=90,fontsize=8)
        ax.axvline(11.5,color='#24334a',lw=1.5);ax.set_title('Contribution by route and month, sorted by Period 2 result')
        fig.colorbar(im,ax=ax,shrink=.65,pad=.02,label='Contribution, thousands')
        finish(fig,'06_route_month_heatmap',pdf,'White cells have no recorded activity. Color scale is shared across all route-months.\n'+common)

        decomp=read('costs_decomposition.csv')
        # Category cost shares, and growth in dollars, with two-period comparisons.
        fig,(ax,bx)=plt.subplots(1,2,figsize=(13,6));cats=['fuel','crew','maintenance','food']
        for j,r in enumerate(costperiod):
            ax.bar([i+(j-.5)*.35 for i in range(4)],[number(r,c+'_cost')/1e6 for c in cats],width=.35,label='Period '+str(j+1),color=[BLUE,TEAL][j])
        ax.set_xticks(range(4),[c.title() for c in cats]);ax.set_ylabel('Millions');ax.legend(frameon=False);ax.set_title('Fuel is the largest recorded cost')
        vals=[(number(costperiod[1],c+'_cost')-number(costperiod[0],c+'_cost'))/1e6 for c in cats]
        bars=bx.barh([c.title() for c in cats],vals,color=RED);bx.bar_label(bars,fmt='%.2f',padding=3);bx.set_xlim(0,max(vals)*1.2)
        bx.set_xlabel('Cost increase, millions');bx.set_title('Fuel and crew lead the increase')
        finish(fig,'07_cost_categories',pdf,'86.4% of total cost growth is associated with more cost events at the Period 1 average cost.\nThe remaining 13.6% includes cost per event and route-mix changes; it is not isolated inflation.')

        mix=read('commercial_revenue_mix.csv'); lookup={(r['period'],r['type']):int(r['revenue_cents']) for r in mix}
        channels=read('commercial_channel.csv'); types=['Extra Baggage','Seat Upgrade','Food & Onboard','Change Fee']
        fig,(ax,bx)=plt.subplots(1,2,figsize=(13,6))
        for j,p in enumerate(['1','2']):
            ax.barh([i+(j-.5)*.33 for i in range(4)],[lookup[(p,t)]/1e8 for t in types],height=.33,label='Period '+p,color=[BLUE,TEAL][j])
        ax.set_yticks(range(4),types);ax.invert_yaxis();ax.set_xlabel('Millions');ax.legend(frameon=False);ax.set_title('Paid extras and fees remain small')
        groups=sorted({r['channel'] for r in channels})
        for j,p in enumerate(['1','2']):
            rows={r['channel']:r for r in channels if r['period']==p}
            vals=[100*int(rows[g]['refund_cents'])/(int(rows[g]['net_cents'])+int(rows[g]['refund_cents'])) for g in groups]
            bx.barh([i+(j-.5)*.33 for i in range(4)],vals,height=.33,label='Period '+p,color=[BLUE,TEAL][j])
        bx.set_yticks(range(4),[g.replace('Online Travel Agency','OTA').replace('Corporate Portal','Corporate') for g in groups]);bx.invert_yaxis()
        bx.set_xlabel('Refund amounts / positive amounts, %');bx.set_title('OTA refund burden is highest')
        finish(fig,'08_extras_refunds',pdf,'Refund burden is an amount ratio, not cancellation rate. Channels may differ in route, traveler and product mix.\nPaid extras: baggage, onboard food and seat upgrades. Change fees are shown separately.')

        fig,(ax,bx)=plt.subplots(1,2,figsize=(13,6))
        for j,p in enumerate(['1','2']):
            rows={r['channel']:r for r in channels if r['period']==p}
            ax.barh([i+(j-.5)*.33 for i in range(4)],[int(rows[g]['net_cents'])/1e8 for g in groups],height=.33,label='Period '+p,color=[BLUE,TEAL][j])
        ax.set_yticks(range(4),[g.replace('Online Travel Agency','OTA') for g in groups]);ax.invert_yaxis();ax.legend(frameon=False);ax.set_xlabel('Net revenue, millions');ax.set_title('Direct Web supplies 40.1% of revenue')
        attachments=read('commercial_attachment_by_channel.csv')
        for j,p in enumerate(['1','2']):
            rows={r['channel']:r for r in attachments if r['period']==p}
            bx.barh([i+(j-.5)*.33 for i in range(4)],[100*int(rows[g]['attached_bookings'])/int(rows[g]['ticket_bookings']) for g in groups],height=.33,label='Period '+p,color=[BLUE,TEAL][j])
        bx.set_yticks(range(4),[g.replace('Online Travel Agency','OTA').replace('Corporate Portal','Corporate') for g in groups]);bx.invert_yaxis();bx.set_xlim(0,45)
        bx.set_xlabel('Ticket bookings with paid extra, %');bx.set_title('Channel attachment differs by little')
        finish(fig,'09_channels',pdf,'Attachment requires a ticket and paid extra on the same booking in the same comparison period.\nChannel ticket-value comparisons adjusted for route/month mix are in the commercial tables and report.')

        sens=read('network_sensitivity.csv')
        fig,ax=plt.subplots(figsize=(13,7));vals=[number(r,'contribution_before_gates')/1e6 for r in sens]
        ax.barh(range(len(sens)),vals,color=[GREY]+[TEAL if v>vals[0] else RED for v in vals[1:]])
        ax.set_yticks(range(len(sens)),[r['scenario'].replace('Revenue +5% and recorded operating cost -5%','Revenue +5%; cost −5%') for r in sens],fontsize=9)
        ax.invert_yaxis();ax.axvline(vals[0],color=GREY,linestyle='--');ax.set_xlim(-65,0);ax.set_xlabel('Period 2 contribution before gates, millions')
        for i,v in enumerate(vals):ax.text(v+.7,i,f'{v:,.2f}',va='center',color='white',fontsize=9)
        ax.set_title('Small commercial gains do not close the recorded deficit',fontsize=15)
        fig.subplots_adjust(left=.30)
        # Wider labels need a custom margin after the shared formatting call.
        fig.text(.02,.018,'Arithmetic sensitivities holding other amounts and activity fixed; these are not forecasts or causal estimates.\nGate charges and all unobserved overhead remain excluded.',fontsize=8,color=GREY)
        fig.subplots_adjust(bottom=.15,top=.90,left=.31,right=.96)
        fig.savefig(CHARTS/'10_sensitivity.png',dpi=180);fig.savefig(CHARTS/'10_sensitivity.svg');pdf.savefig(fig);plt.close(fig)
    print('Created 10 charts as PNG/SVG and a 10-page PDF.')


def export_workbook():
    wb=Workbook();index=wb.active;index.title='Read me'
    index.append(['Airline analysis','Value / explanation'])
    for row in [('Period 1',P1),('Period 2',P2),('Money','Unspecified source currency; cents columns converted to dollars in this workbook'),
      ('Contribution','Net recorded transaction revenue less Crew, Food, Fuel and Maintenance; excludes gates and other overhead'),
      ('Gate scenario','Assumed Sep–Aug mapping; physical gates counted once; shared assigned gates allocated equally'),
      ('Methodology','See ASSUMPTIONS.md and REPORT.md'),('Raw source files','Preserved; verified duplicates removed only from the analysis database')]:index.append(row)
    index.append([]);index.append(['Source table','Workbook tab'])
    used={'Read me'}
    for path in sorted(TABLES.glob('*.csv')):
        stem=path.stem
        base=stem.replace('commercial_','comm_').replace('contribution','contrib').replace('transactions','tx')[:31]
        name=base;i=2
        while name in used:name=base[:28]+f'_{i}';i+=1
        used.add(name);ws=wb.create_sheet(name)
        with path.open(newline='') as f:
            reader=csv.reader(f);headers=next(reader)
            converted=[re.sub('cents$','dollars',h,flags=re.I) for h in headers]
            ws.append(converted)
            for row in reader:
                values=[]
                for h,v in zip(headers,row):
                    if not v:values.append(None)
                    elif re.fullmatch(r'-?\d+(\.\d+)?',v):
                        if h.casefold().endswith('cents'):values.append(float(Decimal(v)/100))
                        elif '.' in v:values.append(float(v))
                        else:values.append(int(v))
                    else:values.append(v)
                ws.append(values)
        ws.freeze_panes='C2' if len(headers)>6 else 'B2';ws.auto_filter.ref=ws.dimensions
        for i,h in enumerate(converted,1):
            ws.column_dimensions[get_column_letter(i)].width=min(28,max(13,len(h)+2))
            moneycol=any(s in h.lower() for s in ['dollars','revenue','contribution','cost','charge','refund_amount','allocation_per_event']) and not any(s in h.lower() for s in ['count','events','pct','change_pct','ratio'])
            for cells in ws.iter_cols(min_col=i,max_col=i,min_row=2):
                for cell in cells:
                    if isinstance(cell.value,(int,float)):
                        cell.number_format='#,##0.00;[Red](#,##0.00)' if moneycol or isinstance(cell.value,float) else '#,##0'
        index.append([path.name,name]);index.cell(index.max_row,2).hyperlink=f"#'{name}'!A1";index.cell(index.max_row,2).style='Hyperlink'
    for ws in wb:
        ws.row_dimensions[1].height=30
        for cell in ws[1]:cell.font=Font(color='FFFFFF',bold=True);cell.fill=PatternFill('solid',fgColor='235789')
    index.column_dimensions['A'].width=52;index.column_dimensions['B'].width=105;index.freeze_panes='B2'
    wb.save(HERE/'analysis_workbook.xlsx')
    print(f'Created workbook with {len(wb.sheetnames)-1} data tables and an index.')


if __name__=='__main__':
    draw_charts()
    export_workbook()
