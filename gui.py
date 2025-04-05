import sys
import asyncio
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QListWidget, QLineEdit,
                             QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QFont
from config_manager import load_accounts, save_accounts
from game_automation import run_account_sync
from stats_processor import generate_charts

class AsyncWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, account):
        super().__init__()
        self.account = account
        self.is_stopped = False  # 添加停止标志

    def run(self):
        loop = asyncio.new_event_loop()  # 创建新的 asyncio 事件循环
        asyncio.set_event_loop(loop)
        try:
            if not self.is_stopped:
                stats = loop.run_until_complete(self.run_game_task())
                if not self.is_stopped:
                    self.finished.emit(stats)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            loop.close()

    async def run_game_task(self):
        return await asyncio.to_thread(run_account_sync, self.account['name'], self.account.get('cookie', {}))

    def stop(self):
        self.is_stopped = True  # 设置停止标志

class MagicDiceGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.accounts = load_accounts() or []
        self.running_workers = []  # 跟踪运行的 worker
        self.initUI()

    def initUI(self):
        self.setWindowTitle("骰子游戏界面")
        self.setGeometry(300, 150, 400, 250)

        self.accountList = QListWidget()
        self.update_account_list()

        self.nameInput = QLineEdit()
        self.addAccountButton = QPushButton("添加账号")
        self.startButton = QPushButton("开始游戏")
        self.stopButton = QPushButton("停止游戏")
        self.statsButton = QPushButton("查看统计")

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("账号名称:"))
        hbox.addWidget(self.nameInput)
        hbox.addWidget(self.addAccountButton)

        vbox = QVBoxLayout()
        vbox.addWidget(self.accountList)
        vbox.addLayout(hbox)
        vbox.addWidget(self.startButton)
        vbox.addWidget(self.stopButton)
        vbox.addWidget(self.statsButton)

        self.setLayout(vbox)

        self.addAccountButton.clicked.connect(self.addAccount)
        self.startButton.clicked.connect(self.start_game)
        self.stopButton.clicked.connect(self.stop_game)
        self.statsButton.clicked.connect(self.view_statistics)  # 修正信号连接

    def addAccount(self):
        name = self.nameInput.text().strip()
        if name and not any(acc.get('name') == name for acc in self.accounts):
            new_account = {'name': name, 'cookie': {}}
            self.accounts.append(new_account)
            self.accountList.addItem(new_account['name'])
            self.save_accounts()
            self.nameInput.clear()
        else:
            QMessageBox.warning(self, "警告", "账号名称已存在或为空！")

    def start_game(self):
        selected_items = self.accountList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个账号！")
            return

        account_name = selected_items[0].text()
        account = next((a for a in self.accounts if a.get('name') == account_name), None)
        if account and 'cookie' in account:
            worker = AsyncWorker(account)
            worker.finished.connect(lambda stats: self.on_game_finished(account, stats))
            worker.error.connect(self.on_game_error)
            worker.start()  # 使用 QThread 的 start() 方法
            self.running_workers.append(worker)
            print(f"Started game for {account_name}")

    def on_game_finished(self, account, stats):
        account['stats'] = stats
        self.save_accounts()
        print(f"Game completed for {account['name']} with stats: {stats}")
        self.running_workers.remove(self.sender())  # 移除已完成的任务

    def on_game_error(self, error):
        print(f"Error in game: {error}")

    def stop_game(self):
        for worker in self.running_workers[:]:  # 复制列表避免修改迭代
            if worker.isRunning():
                worker.stop()  # 设置停止标志
                worker.wait(1000)  # 等待 1 秒，允许优雅退出
                if worker.isRunning():
                    worker.terminate()  # 强制终止
            self.running_workers.remove(worker)
        print("All games stopped")

    def view_statistics(self):
        all_stats = [acc.get('stats', {'wins': 0, 'losses': 0, 'profit': 0}) for acc in self.accounts]
        generate_charts(all_stats)

    def update_account_list(self):
        self.accountList.clear()
        for account in self.accounts:
            self.accountList.addItem(account.get('name', 'Unknown'))

    def save_accounts(self):
        save_accounts(self.accounts)

    def closeEvent(self, event):
        for worker in self.running_workers[:]:
            if worker.isRunning():
                worker.stop()
                worker.wait(1000)
                if worker.isRunning():
                    worker.terminate()
            worker.deleteLater()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MagicDiceGUI()
    gui.show()
    sys.exit(app.exec_())