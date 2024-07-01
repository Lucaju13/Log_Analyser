import sys
import re
import csv
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QLineEdit, QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt

class LogParserApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.intervals = []
        
    def initUI(self):
        self.setWindowTitle('Analyseur de Régulations')
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        self.log_file_label = QLabel('Fichier de logs :')
        self.log_file_path = QLineEdit()
        self.browse_button = QPushButton('Parcourir')
        self.browse_button.clicked.connect(self.browse_file)
        
        self.parse_button = QPushButton('Analyser les logs')
        self.parse_button.clicked.connect(self.parse_logs)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Heure de début', 'Heure de fin', 'Intervalle (secondes)', 'ID de la turbine'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.export_button = QPushButton('Exporter en CSV')
        self.export_button.clicked.connect(self.export_to_csv)
        
        self.clear_button = QPushButton('Effacer le tableau')
        self.clear_button.clicked.connect(self.clear_table)
        
        self.quit_button = QPushButton('Quitter')
        self.quit_button.clicked.connect(self.quit_application)
        
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.log_file_label)
        file_layout.addWidget(self.log_file_path)
        file_layout.addWidget(self.browse_button)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.parse_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.quit_button)
        
        layout.addLayout(file_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
    def browse_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Sélectionner le fichier de logs", "", "Fichiers texte (*.txt);;Tous les fichiers (*)", options=options)
        if file_name:
            self.log_file_path.setText(file_name)
    
    def parse_logs(self):
        log_file = self.log_file_path.text()
        
        events = self.parse_log_file(log_file)
        intervals = self.calculate_intervals(events)
        
        self.intervals.extend(intervals)
        self.update_table()
    
    def parse_log_file(self, log_file):
        start_pattern = r"(\d+-\d+-\d+ \d+:\d+:\d+\.\d+) \+\d+:\d+ \[INF\] \[MuninController\] Regulate : Received for wind turbine (\d+-[A-Z]\d) regulate value : PAUSE DONE"
        stop_pattern = r"(\d+-\d+-\d+ \d+:\d+:\d+\.\d+) \+\d+:\d+ \[INF\] \[MuninController\] Regulate : Received for wind turbine (\d+-[A-Z]\d) regulate value : RUN DONE"
        
        events = []
        
        with open(log_file, 'r') as file:
            for line in file:
                start_match = re.match(start_pattern, line)
                stop_match = re.match(stop_pattern, line)
                
                if start_match:
                    start_time_str = start_match.group(1)
                    turbine_id = start_match.group(2)
                    start_time_obj = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S.%f')
                    events.append((start_time_obj, 'start', turbine_id))
                        
                if stop_match:
                    stop_time_str = stop_match.group(1)
                    turbine_id = stop_match.group(2)
                    stop_time_obj = datetime.strptime(stop_time_str, '%Y-%m-%d %H:%M:%S.%f')
                    events.append((stop_time_obj, 'stop', turbine_id))
        
        # Trier les événements par heure pour calculer les intervalles correctement
        events.sort(key=lambda x: x[0])
        return events
    
    def calculate_intervals(self, events):
        intervals = []
        start_events = {}
    
        for event in events:
            time, event_type, turbine_id = event
            if event_type == 'start':
                start_events[turbine_id] = time
            elif event_type == 'stop' and turbine_id in start_events:
                start_time = start_events.pop(turbine_id)
                interval = (time - start_time).total_seconds()
                if interval >= 0:  # Assurer uniquement des intervalles positifs
                    intervals.append((start_time, time, interval, turbine_id))
        
        return intervals
    
    def update_table(self):
        current_row_count = self.table.rowCount()
        new_row_count = len(self.intervals)
        
        self.table.setRowCount(new_row_count)
        
        for row in range(current_row_count, new_row_count):
            start, stop, interval, turbine_id = self.intervals[row]
            self.table.setItem(row, 0, QTableWidgetItem(start.strftime('%Y-%m-%d %H:%M:%S.%f')))
            self.table.setItem(row, 1, QTableWidgetItem(stop.strftime('%Y-%m-%d %H:%M:%S.%f')))
            self.table.setItem(row, 2, QTableWidgetItem(str(interval)))
            self.table.setItem(row, 3, QTableWidgetItem(turbine_id))
            
            # Make items non-editable
            for col in range(4):
                item = self.table.item(row, col)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)  # Remove the editable flag

    
    def clear_table(self):
        self.table.setRowCount(0)
        self.intervals = []
    
    def export_to_csv(self):
        options = QFileDialog.Options()
        output_file, _ = QFileDialog.getSaveFileName(self, "Enregistrer le fichier CSV", "", "Fichiers CSV (*.csv);;Tous les fichiers (*)", options=options)
        if output_file:
            export_intervals_to_csv(self.intervals, output_file)
            QMessageBox.information(self, "Exportation réussie", "Les intervalles ont été exportés en CSV avec succès")
    
    def quit_application(self):
        choice = QMessageBox.question(self, 'Quitter', "Êtes-vous sûr de vouloir quitter l'application ?", QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.close()
        else:
            pass

def export_intervals_to_csv(intervals, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Heure de début', 'Heure de fin', 'Intervalle (secondes)', 'ID de la turbine']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        
        writer.writeheader()
        for start, stop, interval, turbine_id in intervals:
            writer.writerow({'Heure de début': start.strftime('%Y-%m-%d %H:%M:%S.%f'), 
                             'Heure de fin': stop.strftime('%Y-%m-%d %H:%M:%S.%f'), 
                             'Intervalle (secondes)': interval, 
                             'ID de la turbine': turbine_id})


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LogParserApp()
    ex.show()
    sys.exit(app.exec_())
