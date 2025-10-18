import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import os
from datetime import datetime
import base64
from io import BytesIO

# Configuración de estilo
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class FinancialCharts:
    """
    Generador de gráficos financieros para análisis de ahorro
    """
    
    def __init__(self, output_dir: str = "static/charts"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def create_expense_pie_chart(self, category_totals: Dict, analysis: Dict) -> str:
        """
        Gráfico circular de gastos por categoría
        """
        # Filtrar solo gastos (valores negativos)
        expenses = {k: abs(v) for k, v in category_totals.items() if v < 0}
        
        if not expenses:
            return None
            
        # Crear gráfico con Plotly
        fig = go.Figure(data=[go.Pie(
            labels=list(expenses.keys()),
            values=list(expenses.values()),
            hole=0.4,
            textinfo='label+percent+value',
            texttemplate='%{label}<br>%{percent}<br>%{value:.2f}€',
            hovertemplate='<b>%{label}</b><br>Gasto: %{value:.2f}€<br>Porcentaje: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': f"Distribución de Gastos<br><sub>Total: {analysis['total_expenses']:.2f}€</sub>",
                'x': 0.5,
                'font': {'size': 16}
            },
            font=dict(size=12),
            showlegend=True,
            height=500,
            margin=dict(t=80, b=40, l=40, r=40)
        )
        
        filename = f"expense_pie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        
        return filepath
    
    def create_income_vs_expenses_chart(self, analysis: Dict) -> str:
        """
        Gráfico de barras comparando ingresos vs gastos
        """
        categories = ['Ingresos', 'Gastos', 'Balance']
        values = [analysis['total_income'], -analysis['total_expenses'], analysis['balance']]
        colors = ['#2E8B57', '#DC143C', '#4169E1' if analysis['balance'] >= 0 else '#FF6347']
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                marker_color=colors,
                text=[f'{v:+.2f}€' for v in values],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>%{y:+.2f}€<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title={
                'text': "Resumen Financiero<br><sub>Ingresos vs Gastos vs Balance</sub>",
                'x': 0.5,
                'font': {'size': 16}
            },
            yaxis_title="Cantidad (€)",
            font=dict(size=12),
            height=400,
            margin=dict(t=80, b=40, l=40, r=40)
        )
        
        # Línea de referencia en 0
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        filename = f"income_expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        
        return filepath
    
    def create_50_30_20_budget_chart(self, profile: Dict) -> str:
        """
        Gráfico del presupuesto 50-30-20 (ideal vs real)
        """
        categories = ['Essentials (50%)', 'Ocio (30%)', 'Ahorros (20%)']
        
        # Valores ideales
        ideal_values = [
            profile['ideal_essentials'],
            profile['ideal_discretionary'], 
            profile['ideal_savings']
        ]
        
        # Valores reales
        actual_values = [
            profile['actual_essentials'],
            profile['actual_discretionary'],
            profile['actual_savings']
        ]
        
        fig = go.Figure()
        
        # Barras ideales
        fig.add_trace(go.Bar(
            name='Ideal',
            x=categories,
            y=ideal_values,
            marker_color='lightblue',
            opacity=0.7,
            text=[f'{v:.2f}€' for v in ideal_values],
            textposition='auto'
        ))
        
        # Barras reales
        fig.add_trace(go.Bar(
            name='Real',
            x=categories,
            y=actual_values,
            marker_color='darkblue',
            opacity=0.9,
            text=[f'{v:.2f}€' for v in actual_values],
            textposition='auto'
        ))
        
        fig.update_layout(
            title={
                'text': "Presupuesto 50-30-20<br><sub>Comparación Ideal vs Real</sub>",
                'x': 0.5,
                'font': {'size': 16}
            },
            yaxis_title="Cantidad (€)",
            barmode='group',
            font=dict(size=12),
            height=400,
            margin=dict(t=80, b=40, l=40, r=40)
        )
        
        filename = f"budget_50_30_20_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        
        return filepath
    
    def create_savings_trend_chart(self, analysis: Dict, profile: Dict) -> str:
        """
        Gráfico de tendencia de ahorro con recomendaciones
        """
        # Simular datos mensuales (en un caso real vendrían de datos históricos)
        months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
        current_balance = analysis['balance']
        
        # Proyección basada en el perfil actual
        if profile['profile_type'] == 'Ahorrador constante':
            trend = np.linspace(current_balance * 0.7, current_balance, 6)
        elif profile['profile_type'] == 'Ahorrador':
            trend = np.linspace(current_balance * 0.6, current_balance, 6)
        else:
            trend = np.linspace(current_balance * 0.4, current_balance, 6)
        
        # Meta de ahorro (20% del ingreso mensual)
        monthly_income = analysis['total_income'] / 6  # Asumiendo 6 meses
        savings_goal = np.cumsum([monthly_income * 0.2] * 6)
        
        fig = go.Figure()
        
        # Línea de tendencia actual
        fig.add_trace(go.Scatter(
            x=months,
            y=trend,
            mode='lines+markers',
            name='Ahorro Actual',
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ))
        
        # Meta de ahorro
        fig.add_trace(go.Scatter(
            x=months,
            y=savings_goal,
            mode='lines+markers',
            name='Meta 20%',
            line=dict(color='green', width=3, dash='dash'),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title={
                'text': "Tendencia de Ahorro<br><sub>Actual vs Meta Recomendada</sub>",
                'x': 0.5,
                'font': {'size': 16}
            },
            yaxis_title="Ahorro Acumulado (€)",
            xaxis_title="Mes",
            font=dict(size=12),
            height=400,
            margin=dict(t=80, b=40, l=40, r=40)
        )
        
        filename = f"savings_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        
        return filepath
    
    def create_expense_volatility_chart(self, analysis: Dict, profile: Dict) -> str:
        """
        Gráfico de volatilidad de gastos
        """
        volatility = analysis['expense_volatility']
        
        # Categorías de volatilidad
        categories = ['Muy Baja', 'Baja', 'Media', 'Alta', 'Muy Alta']
        values = [0, 50, 100, 150, 200]
        colors = ['green', 'lightgreen', 'yellow', 'orange', 'red']
        
        # Encontrar la categoría actual
        current_category = 0
        for i, threshold in enumerate(values):
            if volatility <= threshold:
                current_category = i
                break
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=[1] * len(categories),
                marker_color=colors,
                opacity=0.3,
                showlegend=False
            )
        ])
        
        # Marcar la categoría actual
        fig.add_trace(go.Scatter(
            x=[categories[current_category]],
            y=[1],
            mode='markers',
            marker=dict(
                size=20,
                color='black',
                symbol='x'
            ),
            name=f'Tu nivel: {volatility:.2f}€'
        ))
        
        fig.update_layout(
            title={
                'text': f"Volatilidad de Gastos<br><sub>Tu nivel: {volatility:.2f}€ ({categories[current_category]})</sub>",
                'x': 0.5,
                'font': {'size': 16}
            },
            yaxis=dict(visible=False),
            xaxis_title="Nivel de Volatilidad",
            font=dict(size=12),
            height=300,
            margin=dict(t=80, b=40, l=40, r=40)
        )
        
        filename = f"expense_volatility_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        
        return filepath
    
    def create_savings_recommendations_chart(self, profile: Dict, analysis: Dict) -> str:
        """
        Gráfico de recomendaciones de ahorro personalizadas
        """
        recommendations = []
        savings_potential = []
        
        # Calcular potencial de ahorro por categoría
        if profile['actual_essentials'] > profile['ideal_essentials']:
            recommendations.append('Reducir gastos esenciales')
            savings_potential.append(profile['actual_essentials'] - profile['ideal_essentials'])
        
        if profile['actual_discretionary'] > profile['ideal_discretionary']:
            recommendations.append('Reducir gastos de ocio')
            savings_potential.append(profile['actual_discretionary'] - profile['ideal_discretionary'])
        
        if analysis['top_expense_category']:
            top_amount = analysis['top_expense_amount']
            recommendations.append(f'Optimizar {analysis["top_expense_category"]}')
            savings_potential.append(top_amount * 0.15)  # 15% de reducción
        
        if not recommendations:
            recommendations = ['Mantener disciplina actual']
            savings_potential = [0]
        
        fig = go.Figure(data=[
            go.Bar(
                x=recommendations,
                y=savings_potential,
                marker_color='lightcoral',
                text=[f'{v:.2f}€' for v in savings_potential],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Potencial de ahorro: %{y:.2f}€<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title={
                'text': "Recomendaciones de Ahorro<br><sub>Potencial de ahorro mensual</sub>",
                'x': 0.5,
                'font': {'size': 16}
            },
            yaxis_title="Potencial de Ahorro (€)",
            font=dict(size=12),
            height=400,
            margin=dict(t=80, b=40, l=40, r=40)
        )
        
        filename = f"savings_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        
        return filepath
    
    def create_profile_radar_chart(self, profile: Dict) -> str:
        """
        Gráfico radar del perfil financiero
        """
        # Métricas normalizadas (0-100)
        metrics = ['Ahorro', 'Disciplina', 'Estabilidad', 'Crecimiento']
        
        # Calcular scores basados en el perfil
        savings_score = min(100, (profile['actual_savings'] / profile['ideal_savings']) * 100) if profile['ideal_savings'] > 0 else 0
        discipline_score = 100 - min(100, profile['expense_volatility'] / 2)  # Menos volatilidad = más disciplina
        stability_score = 100 - min(100, abs(profile['expense_ratio'] - 80) / 2)  # Ratio ideal ~80%
        growth_score = min(100, (profile['actual_savings'] / profile['ideal_savings']) * 100) if profile['ideal_savings'] > 0 else 0
        
        values = [savings_score, discipline_score, stability_score, growth_score]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metrics,
            fill='toself',
            name='Tu Perfil',
            line_color='blue',
            fillcolor='rgba(0, 100, 200, 0.3)'
        ))
        
        # Línea de referencia (perfil ideal)
        ideal_values = [80, 80, 80, 80]
        fig.add_trace(go.Scatterpolar(
            r=ideal_values,
            theta=metrics,
            fill='toself',
            name='Perfil Ideal',
            line_color='green',
            fillcolor='rgba(0, 200, 100, 0.1)',
            opacity=0.5
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            title={
                'text': f"Perfil Financiero: {profile['profile_type']}<br><sub>Análisis multidimensional</sub>",
                'x': 0.5,
                'font': {'size': 16}
            },
            font=dict(size=12),
            height=500,
            margin=dict(t=80, b=40, l=40, r=40)
        )
        
        filename = f"profile_radar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        
        return filepath
    
    def generate_all_charts(self, analysis: Dict, profile: Dict) -> Dict[str, str]:
        """
        Genera todos los gráficos y retorna un diccionario con las rutas
        """
        charts = {}
        
        try:
            charts['expense_pie'] = self.create_expense_pie_chart(analysis['category_totals'], analysis)
            charts['income_expenses'] = self.create_income_vs_expenses_chart(analysis)
            charts['budget_50_30_20'] = self.create_50_30_20_budget_chart(profile)
            charts['savings_trend'] = self.create_savings_trend_chart(analysis, profile)
            charts['expense_volatility'] = self.create_expense_volatility_chart(analysis, profile)
            charts['savings_recommendations'] = self.create_savings_recommendations_chart(profile, analysis)
            charts['profile_radar'] = self.create_profile_radar_chart(profile)
            
        except Exception as e:
            print(f"Error generando gráficos: {e}")
            
        return charts
    
    def create_savings_guide_chart(self, profile: Dict) -> str:
        """
        Gráfico guía de ahorro paso a paso
        """
        steps = [
            "1. Analiza tu situación actual",
            "2. Establece metas realistas", 
            "3. Crea un presupuesto",
            "4. Automatiza ahorros",
            "5. Reduce gastos innecesarios",
            "6. Invierte el exceso",
            "7. Revisa y ajusta"
        ]
        
        # Scores de progreso basados en el perfil
        if profile['profile_type'] == 'Ahorrador constante':
            progress = [100, 100, 100, 80, 90, 60, 70]
        elif profile['profile_type'] == 'Ahorrador':
            progress = [100, 90, 80, 70, 60, 40, 50]
        elif profile['profile_type'] == 'Equilibrado':
            progress = [100, 70, 60, 50, 40, 20, 30]
        else:
            progress = [100, 40, 30, 20, 10, 5, 15]
        
        fig = go.Figure(data=[
            go.Bar(
                x=steps,
                y=progress,
                marker_color='lightgreen',
                text=[f'{p}%' for p in progress],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Progreso: %{y}%<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title={
                'text': "Guía de Ahorro - Tu Progreso<br><sub>Pasos para mejorar tus finanzas</sub>",
                'x': 0.5,
                'font': {'size': 16}
            },
            yaxis_title="Progreso (%)",
            font=dict(size=10),
            height=500,
            margin=dict(t=80, b=100, l=40, r=40),
            xaxis=dict(tickangle=45)
        )
        
        filename = f"savings_guide_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        
        return filepath
