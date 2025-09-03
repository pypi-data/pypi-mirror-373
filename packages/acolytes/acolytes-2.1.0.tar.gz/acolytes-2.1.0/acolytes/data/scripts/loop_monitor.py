#!/usr/bin/env python3
"""
ACOLYTES LOOP MONITOR - Visualización en Tiempo Real
=====================================================

Monitorea el sistema ACOLYTES LOOP mostrando:
- Estado actual de todos los quests
- Quién tiene el turno
- Últimos cambios
- Mensajes entre agentes

Uso: python loop_monitor.py [quest_id]
"""

import sqlite3
import json
import time
import sys
import os
from datetime import datetime
from pathlib import Path


class LoopMonitor:
    def __init__(self, db_path=".claude/memory/project.db"):
        self.db_path = db_path
        self.refresh_interval = 2  # Actualizar cada 2 segundos
        
    def clear_screen(self):
        """Limpiar pantalla para actualización"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def get_active_quests(self):
        """Obtener todos los quests activos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT quest_id, quest_name, quest_phase, status, 
                   current_agent, recruited, broadcast,
                   datetime(created_at, 'unixepoch', 'localtime') as created
            FROM loop_quests
            WHERE status NOT IN ('completed', 'failed', 'timeout')
            ORDER BY quest_id DESC
        """)
        
        quests = cursor.fetchall()
        conn.close()
        return quests
        
    def get_quest_details(self, quest_id):
        """Obtener detalles específicos de un quest"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Quest info
        cursor.execute("""
            SELECT * FROM loop_quests WHERE quest_id = ?
        """, (quest_id,))
        quest = cursor.fetchone()
        
        # Recent status changes
        cursor.execute("""
            SELECT old_agent, new_agent, old_status, new_status,
                   datetime(changed_at, 'unixepoch', 'localtime') as when_changed,
                   loop_count, message
            FROM loop_status_changes
            WHERE quest_id = ?
            ORDER BY id DESC
            LIMIT 10
        """, (quest_id,))
        changes = cursor.fetchall()
        
        conn.close()
        return quest, changes
        
    def format_time_ago(self, timestamp_str):
        """Formatear tiempo transcurrido"""
        if not timestamp_str:
            return "never"
        try:
            # Parse the datetime string
            past = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            diff = now - past
            
            if diff.seconds < 60:
                return f"{diff.seconds}s ago"
            elif diff.seconds < 3600:
                return f"{diff.seconds // 60}m ago"
            else:
                return f"{diff.seconds // 3600}h ago"
        except:
            return timestamp_str
            
    def display_dashboard(self, quest_id=None):
        """Mostrar dashboard principal"""
        self.clear_screen()
        
        print("=" * 80)
        print("🔄 ACOLYTES LOOP MONITOR - SISTEMA DE COMUNICACIÓN ETERNA 🔄".center(80))
        print("=" * 80)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(80))
        print("=" * 80)
        
        if quest_id:
            # Monitoreo de quest específico
            self.display_quest_detail(quest_id)
        else:
            # Vista general de todos los quests
            self.display_all_quests()
            
    def display_all_quests(self):
        """Mostrar todos los quests activos"""
        quests = self.get_active_quests()
        
        if not quests:
            print("\n📭 No hay quests activos en este momento")
            print("\n💡 Crea un quest para ver el sistema en acción")
            return
            
        print("\n📋 QUESTS ACTIVOS:\n")
        
        for quest in quests:
            quest_id = quest['quest_id']
            name = quest['quest_name']
            status = quest['status']
            current = quest['current_agent']
            phase = quest['quest_phase']
            updated = self.format_time_ago(quest['created'])
            
            # Determinar emoji según estado
            if status == 'working':
                status_emoji = "⚙️"
            elif status == 'waiting':
                status_emoji = "⏳"
            elif status == 'reviewing':
                status_emoji = "🔍"
            else:
                status_emoji = "❓"
                
            print(f"  {status_emoji} Quest #{quest_id}: {name} (Phase {phase})")
            print(f"     Status: {status.upper()} | Turno: {current} | Actualizado: {updated}")
            
            # Mostrar mensaje actual
            try:
                broadcast = json.loads(quest['broadcast'])
                msg = broadcast.get('message', '')[:60] + "..."
                print(f"     📨 Mensaje: {msg}")
            except:
                pass
                
            # Mostrar agentes reclutados
            try:
                recruited = json.loads(quest['recruited'])
                print(f"     👥 Equipo: {', '.join(recruited)}")
            except:
                pass
                
            print()
            
    def display_quest_detail(self, quest_id):
        """Mostrar detalles de un quest específico"""
        quest, changes = self.get_quest_details(quest_id)
        
        if not quest:
            print(f"\n❌ Quest #{quest_id} no encontrado")
            return
            
        # Info principal
        print(f"\n🎯 QUEST #{quest_id}: {quest['quest_name']}")
        print(f"📊 Phase: {quest['quest_phase']} | Status: {quest['status'].upper()}")
        
        # Agentes y turno actual
        try:
            recruited = json.loads(quest['recruited'])
            current = quest['current_agent']
            
            print(f"\n👥 AGENTES EN EL LOOP:")
            for agent in recruited:
                if agent == current:
                    print(f"   ➡️ {agent} 🟢 [TURNO ACTUAL]")
                else:
                    print(f"      {agent} 💤 [esperando...]")
        except:
            pass
            
        # Mensaje actual
        try:
            broadcast = json.loads(quest['broadcast'])
            print(f"\n📬 MENSAJE ACTUAL:")
            print(f"   Para: {broadcast.get('to', 'unknown')}")
            print(f"   Contenido: {broadcast.get('message', 'empty')[:200]}")
        except:
            pass
            
        # Historial de cambios
        if changes:
            print(f"\n📜 HISTORIAL RECIENTE:")
            for change in changes[:5]:  # Mostrar últimos 5
                when = self.format_time_ago(change['when_changed'])
                old_agent = change['old_agent'] or "none"
                new_agent = change['new_agent'] or "none"
                old_status = change['old_status'] or "none"
                new_status = change['new_status'] or "none"
                
                if old_agent != new_agent:
                    print(f"   [{when}] 🔄 Turno: {old_agent} → {new_agent}")
                if old_status != new_status:
                    print(f"   [{when}] 📊 Estado: {old_status} → {new_status}")
                    
        # Resultado si existe
        if quest['result']:
            try:
                result = json.loads(quest['result'])
                print(f"\n✅ RESULTADO FINAL:")
                print(f"   {json.dumps(result, indent=2)}")
            except:
                pass
                
    def monitor_loop(self, quest_id=None):
        """Loop principal de monitoreo"""
        print("Iniciando monitor... Presiona Ctrl+C para salir")
        time.sleep(1)
        
        try:
            while True:
                self.display_dashboard(quest_id)
                
                # Instrucciones
                print("\n" + "=" * 80)
                if quest_id:
                    print("📍 Monitoreando Quest específico | Ctrl+C para salir")
                else:
                    print("📍 Vista general | Para monitorear un quest: python loop_monitor.py <quest_id>")
                print(f"🔄 Actualizando cada {self.refresh_interval} segundos...")
                
                time.sleep(self.refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 Monitor detenido")
            
    def show_completed_quests(self):
        """Mostrar quests completados (para análisis)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT quest_id, quest_name, status,
                   datetime(created_at, 'unixepoch', 'localtime') as started,
                   datetime(created_at, 'unixepoch', 'localtime') as ended,
                   result
            FROM loop_quests
            WHERE status IN ('completed', 'failed', 'timeout')
            ORDER BY quest_id DESC
            LIMIT 10
        """)
        
        completed = cursor.fetchall()
        conn.close()
        
        if completed:
            print("\n🏁 QUESTS COMPLETADOS RECIENTEMENTE:")
            for q in completed:
                status_emoji = "✅" if q['status'] == 'completed' else "❌"
                print(f"  {status_emoji} #{q['quest_id']}: {q['quest_name']}")
                print(f"     Inicio: {q['started']} | Fin: {q['ended']}")
                if q['result']:
                    try:
                        result = json.loads(q['result'])
                        print(f"     Resultado: {str(result)[:100]}")
                    except:
                        pass
                print()


def main():
    monitor = LoopMonitor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--completed":
            # Mostrar quests completados
            monitor.show_completed_quests()
        else:
            # Monitorear quest específico
            try:
                quest_id = int(sys.argv[1])
                monitor.monitor_loop(quest_id)
            except ValueError:
                print(f"❌ ID de quest inválido: {sys.argv[1]}")
                print("Uso: python loop_monitor.py [quest_id]")
    else:
        # Monitorear todos los quests
        monitor.monitor_loop()


if __name__ == "__main__":
    main()