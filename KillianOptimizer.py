import customtkinter as ctk
import subprocess
import ctypes
import sys
import winreg
import threading
import platform
import psutil
import os
import time
import shutil # Dosya silme işlemleri için eklendi

# --- [ARSENAL] SERVİS LİSTESİ (GÜNCELLENMİŞ TAM LİSTE - AYNEN KORUNDU) ---
# Telemetri, Takip ve Gereksiz Arka Plan İşlemleri
LIST_TELEMETRY = [
    "DiagTrack", "dmwappushservice", "WerSvc", "PcaSvc", "RetailDemo", 
    "bthserv", "DcpSvc", "lfsvc", "MapsBroker", "SensorService", 
    "SensorDataService", "SensrSvc", "WbioSvc", "BiometricService", 
    "ActivityMonitor", "WpcMonSvc", "Uhssvc", "WaaSMedicSvc",
    "WdiSystemHost", "WdiServiceHost" 
]

# Sistem Şişkinliği (Bloatware)
LIST_BLOAT = [
    "SysMain", "WSearch", "Spooler", "PrintNotify", "Themes", 
    "TabletInputService", "TouchKeyboard", "TextInputManagementService", 
    "StiSvc", "WiaRpc", "WalletService", "PhoneSvc", "SmsRouter", 
    "WpnService", "WpnUserService", "CscService", "defragsvc", 
    "SemgrSvc", "LanmanServer", "TrkWks", "W32Time",
    "OneSyncSvc", "NgcSvc", "NgcCtnrSvc"
]

# Xbox ve Oyun (Store Kullanmayanlar İçin)
LIST_XBOX = [
    "XblAuthManager", "XblGameSave", "XboxNetApiSvc", "XboxGipSvc", 
    "BcastDVRUserService", "GamingServices", "GamingServicesNet", "XblGameSave"
]

# UWP ve Modern Uygulama Servisleri
LIST_UWP = [
    "ClipSVC", "AppXSvc", "LicenseManager", "StateRepository", 
    "AppReadiness", "AppVClient", "AppVShNotify", "PushToInstall", 
    "InstallService", "ClientLicense", "EntAppSvc", "DsSvc"
]

# Ağ Paylaşımı ve Uzak Erişim (Ping & Latency İçin)
LIST_REMOTE = [
    "LanmanWorkstation", "LmHosts", "RemoteRegistry", "TermService", 
    "UmRdpService", "SessionEnv", "SharedAccess", "SSDPSRV", 
    "upnphost", "fdPHost", "FDResPub", "NetTcpPortSharing", 
    "NcdAutoSetup", "RasMan", "SstpSvc", "PimIndexMaintenanceSvc",
    "NetBT"
]

# Windows Update (Servisler)
LIST_UPDATE_SERVICES = [
    "wuauserv", "UsoSvc", "WaaSMedicSvc", "Bits", "Dosvc", "WIMMount"
]

# Windows Defender (Servisler)
LIST_DEFENDER_SERVICES = [
    "WinDefend", "Sense", "WdNisSvc", "WdBoot", "WdFilter", 
    "SecurityHealthService", "SgrmBroker", "SgrmAgent"
]


class KillianOptimizer(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # PENCERE AYARLARI (SOFT PREMIUM DARK)
        self.title("KILLIAN OPTIMIZER") 
        self.geometry("900x900") # Temizleme butonu sığsın diye biraz uzattım
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        # Soft Gece Mavisi / Koyu Gri (Catppuccin Base)
        self.configure(fg_color="#1E1E2E")

        self.service_vars = {} 
        self.reg_vars = {}

        self.setup_ui()

    def get_system_info(self):
        try:
            cpu = platform.processor()
            ram = f"{round(psutil.virtual_memory().total / (1024**3))} GB"
            os_ver = f"{platform.system()} {platform.release()}"
            return f"CPU: {cpu}  |  RAM: {ram}  |  OS: {os_ver}"
        except:
            return "Sistem Bilgisi Bekleniyor..."

    def setup_ui(self):
        # --- 1. SYSTEM INFORMER (SOFT STİL) ---
        self.info_frame = ctk.CTkFrame(self, fg_color="#313244", corner_radius=0, height=45, border_width=1, border_color="#45475A")
        self.info_frame.pack(fill="x", side="top")
        
        lbl_info_head = ctk.CTkLabel(self.info_frame, text=" SYSTEM INFORMER ", font=("Consolas", 11, "bold"), 
                                     fg_color="#45475A", text_color="#A6E3A1", corner_radius=4) # Soft Nane Yeşili
        lbl_info_head.pack(side="left", padx=15, pady=8)

        self.lbl_sys_info = ctk.CTkLabel(self.info_frame, text=self.get_system_info(), font=("Consolas", 12), text_color="#CDD6F4") # Soft Beyaz/Gri
        self.lbl_sys_info.pack(side="right", padx=20)

        # --- 2. HEADER (İMZA) ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(25, 15))

        ctk.CTkLabel(self.header_frame, text="KILLIAN OPTIMIZER", 
                     font=("Orbitron", 32, "bold"), text_color="#89B4FA").pack() # Soft Pastel Mavi
        
        ctk.CTkLabel(self.header_frame, text="BY AKIF YALCIN", 
                     font=("Orbitron", 14), text_color="#A6ADC8").pack()

        # --- 3. SEKMELER (SOFT RENKLER) ---
        self.tabview = ctk.CTkTabview(self, width=840, height=550, fg_color="#313244", 
                                      segmented_button_selected_color="#89B4FA", # Seçili Tab Soft Mavi
                                      segmented_button_selected_hover_color="#749DD0",
                                      segmented_button_unselected_color="#181825",
                                      text_color="#11111B") # Seçili yazı koyu olsun ki okunsun
        self.tabview.pack(pady=10)

        self.tab_services = self.tabview.add("SERVİSLER (KILL LIST)")
        self.tab_security = self.tabview.add("GÜVENLİK & UPDATE")
        self.tab_latency = self.tabview.add("TIMER & LATENCY")

        self.setup_services_tab()
        self.setup_security_tab()
        self.setup_latency_tab()

        # --- 4. ALT PANEL (ACTION BUTTON) ---
        self.btn_apply = ctk.CTkButton(self, text="YAPILANDIRMAYI BAŞLAT", font=("Orbitron", 18, "bold"), 
                                       fg_color="#F38BA8", hover_color="#D97E96", height=65, corner_radius=8, # Soft Pastel Kırmızı
                                       text_color="#11111B", # Buton yazısı koyu
                                       command=self.start_optimization)
        self.btn_apply.pack(fill="x", padx=40, pady=(15, 25))

    # --- SEKME 1: SERVİS LİSTESİ ---
    def setup_services_tab(self):
        self.scroll_srv = ctk.CTkScrollableFrame(self.tab_services, width=800, height=420, fg_color="transparent")
        self.scroll_srv.pack(fill="both", expand=True)

        self.add_category(self.scroll_srv, "1. TELEMETRİ & İZLEME", LIST_TELEMETRY)
        self.add_category(self.scroll_srv, "2. SİSTEM ŞİŞKİNLİĞİ", LIST_BLOAT)
        self.add_category(self.scroll_srv, "3. XBOX & GAMING", LIST_XBOX)
        self.add_category(self.scroll_srv, "4. UWP SERVİSLERİ", LIST_UWP)
        self.add_category(self.scroll_srv, "5. AĞ & UZAK ERİŞİM", LIST_REMOTE)
        
        self.add_category(self.scroll_srv, "6. WINDOWS UPDATE SERVİSLERİ", LIST_UPDATE_SERVICES)
        self.add_category(self.scroll_srv, "7. DEFENDER SERVİSLERİ", LIST_DEFENDER_SERVICES)

        btn_frame = ctk.CTkFrame(self.tab_services, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        ctk.CTkButton(btn_frame, text="Tümünü Seç", width=120, fg_color="#45475A", hover_color="#585B70", command=self.select_all_services).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Seçimi Temizle", width=120, fg_color="#45475A", hover_color="#585B70", command=self.deselect_all_services).pack(side="right", padx=5)

    def add_category(self, parent, title, list_data):
        ctk.CTkLabel(parent, text=title, font=("Consolas", 13, "bold"), text_color="#A6E3A1", anchor="w").pack(fill="x", pady=(15, 5)) # Soft Yeşil Başlıklar
        for srv in list_data:
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(parent, text=srv, variable=var, font=("Consolas", 12), text_color="#CDD6F4",
                                 checkbox_width=20, checkbox_height=20, border_color="#585B70", hover_color="#89B4FA", fg_color="#89B4FA") # Soft Mavi Tikler
            cb.pack(fill="x", pady=3, padx=15)
            self.service_vars[srv] = var

    # --- SEKME 2: GÜVENLİK ---
    def setup_security_tab(self):
        frame = ctk.CTkFrame(self.tab_security, fg_color="transparent")
        frame.pack(fill="both", padx=40, pady=20)

        # Geri Yükleme
        ctk.CTkLabel(frame, text="SİSTEM GÜVENLİĞİ", font=("Orbitron", 18, "bold"), anchor="w", text_color="#89B4FA").pack(fill="x", pady=(0, 10))
        self.btn_restore = ctk.CTkButton(frame, text="SİSTEM GERİ YÜKLEME NOKTASI OLUŞTUR", 
                                         fg_color="#313244", border_width=1, border_color="#A6E3A1", hover_color="#40504B", height=45,
                                         font=("Arial", 12, "bold"), text_color="#A6E3A1",
                                         command=self.create_restore_point)
        self.btn_restore.pack(fill="x", pady=5)
        ctk.CTkLabel(frame, text="İşleme başlamadan önce mutlaka bir kez tıklayın.", text_color="#A6ADC8", font=("Arial", 10)).pack()

        # Registry Tweaks
        ctk.CTkLabel(frame, text="LOBOTOMİ AYARLARI", font=("Orbitron", 18, "bold"), anchor="w", text_color="#F38BA8").pack(fill="x", pady=(25, 10))
        
        self.reg_vars["update"] = ctk.BooleanVar(value=True)
        self.sw_update = ctk.CTkSwitch(frame, text="WINDOWS UPDATE'İ KAYIT DEFTERİNDEN SİL (NO AUTO UPDATE)", text_color="#CDD6F4",
                                       variable=self.reg_vars["update"], font=("Arial", 12, "bold"), progress_color="#F38BA8")
        self.sw_update.pack(fill="x", pady=10)

        self.reg_vars["defender"] = ctk.BooleanVar(value=True)
        self.sw_defender = ctk.CTkSwitch(frame, text="DEFENDER LOBOTOMİ (ANTI-SPYWARE & REALTIME KAPAT)", text_color="#CDD6F4",
                                         variable=self.reg_vars["defender"], font=("Arial", 12, "bold"), progress_color="#F38BA8")
        self.sw_defender.pack(fill="x", pady=10)

        # --- [YENİ EKLENEN KISIM] DERİN TEMİZLİK ---
        ctk.CTkLabel(frame, text="SİSTEM TEMİZLİĞİ (JUNK CLEANER)", font=("Orbitron", 18, "bold"), anchor="w", text_color="#FAB387").pack(fill="x", pady=(25, 10)) # Soft Şeftali/Turuncu
        
        # Buton yazısını yeni temizlenecek alanları gösterecek şekilde güncelledim
        self.btn_clean = ctk.CTkButton(frame, text="GEREKSİZ DOSYALARI TEMİZLE (PREFETCH, TEMP, CACHE, LOGS)", 
                                       fg_color="#313244", border_width=1, border_color="#FAB387", hover_color="#4A3A36", height=50,
                                       font=("Arial", 12, "bold"), text_color="#FAB387",
                                       command=self.start_cleaner_thread)
        self.btn_clean.pack(fill="x", pady=5)

    # --- SEKME 3: LATENCY ---
    def setup_latency_tab(self):
        frame = ctk.CTkFrame(self.tab_latency, fg_color="transparent")
        frame.pack(expand=True)

        ctk.CTkLabel(frame, text="KERNEL TIMER RESOLUTION", font=("Orbitron", 24, "bold"), text_color="#89B4FA").pack(pady=20)
        
        self.lbl_timer = ctk.CTkLabel(frame, text="DURUM: BEKLEMEDE", font=("Consolas", 16), text_color="#FAB387")
        self.lbl_timer.pack(pady=10)

        self.btn_timer = ctk.CTkButton(frame, text="0.50ms MODUNU AKTİF ET", 
                                       command=self.set_timer_max, width=380, height=65, corner_radius=10,
                                       font=("Orbitron", 16, "bold"), fg_color="#313244", border_width=1, border_color="#89B4FA", text_color="#89B4FA", hover_color="#2A324A")
        self.btn_timer.pack(pady=30)
        ctk.CTkLabel(frame, text="Input lag (Giriş gecikmesi) azalır.\nOyuna girmeden önce aktif edin.", font=("Arial", 12), text_color="#A6ADC8").pack()

    # --- OPERASYON FONKSİYONLARI ---
    def select_all_services(self):
        for var in self.service_vars.values(): var.set(True)

    def deselect_all_services(self):
        for var in self.service_vars.values(): var.set(False)

    def create_restore_point(self):
        self.btn_restore.configure(text="OLUŞTURULUYOR... (BEKLEYİN)", state="disabled")
        threading.Thread(target=self._restore_thread).start()

    def _restore_thread(self):
        try:
            cmd = r'powershell.exe Checkpoint-Computer -Description "KillianOptimizer" -RestorePointType "MODIFY_SETTINGS"'
            subprocess.run(cmd, shell=True)
            self.btn_restore.configure(text="BAŞARILI: YEDEK ALINDI", fg_color="#A6E3A1", text_color="#11111B", state="normal")
        except:
            self.btn_restore.configure(text="HATA: YEDEK ALINAMADI", fg_color="#F38BA8", text_color="#11111B")

    # --- [YENİ] CLEANER FONKSİYONLARI ---
    def start_cleaner_thread(self):
        self.btn_clean.configure(text="TEMİZLENİYOR... (LÜTFEN BEKLEYİN)", state="disabled")
        threading.Thread(target=self._cleaner_logic).start()

    def _cleaner_logic(self):
        # Güvenli çevre değişkenleri (Eğer bulunamazsa varsayılan C:\Windows dizinlerine düşer)
        system_root = os.environ.get('SystemRoot', 'C:\\Windows')
        local_appdata = os.environ.get('LOCALAPPDATA', 'C:\\Users\\Default\\AppData\\Local')

        # Temizlenecek Klasörler (HİÇBİR ŞEY SİLİNMEDİ, YENİ YOLLAR EKLENDİ)
        folders_to_clean = [
            os.path.join(system_root, 'Prefetch'),  # C:\Windows\Prefetch
            os.path.join(system_root, 'Temp'),      # C:\Windows\Temp
            os.environ.get('TEMP'),                 # %TEMP% (AppData/Local/Temp)
            # --- DERİN TEMİZLİK İÇİN EKLENEN YENİ YOLLAR ---
            os.path.join(system_root, 'SoftwareDistribution', 'Download'), # Windows Update Kalıntıları
            os.path.join(system_root, 'ServiceProfiles', 'NetworkService', 'AppData', 'Local', 'Microsoft', 'Windows', 'DeliveryOptimization', 'Cache'), # Teslim İyileştirme (Delivery Optimization)
            os.path.join(local_appdata, 'D3DSCache'), # DirectX Shader Cache
            os.path.join(system_root, 'Logs', 'CBS'), # Windows Hata ve Sistem Logları (CBS)
            os.path.join(system_root, 'Panther'), # Eski Windows Kurulum Kalıntıları
            os.path.join(local_appdata, 'Microsoft', 'Windows', 'WER'), # Windows Hata Raporları (WER)
            os.path.join(local_appdata, 'Microsoft', 'Windows', 'Explorer') # Küçük Resim (Thumbnail) Önbellekleri
        ]

        deleted_files = 0
        
        for folder in folders_to_clean:
            # Klasör mevcutsa ve bir string ise (os.environ.get None dönebilir)
            if folder and os.path.exists(folder):
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                            deleted_files += 1
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                            deleted_files += 1
                    except Exception as e:
                        pass # Dosya kullanımda ise (Örn: aktif log dosyası) hata verme, pas geç

        time.sleep(1)
        self.btn_clean.configure(text=f"TEMİZLİK BİTTİ ({deleted_files} ÖĞE SİLİNDİ)", fg_color="#A6E3A1", text_color="#11111B", state="normal")
        time.sleep(3)
        # Buton yazısı başa dönerken de yeni halini koruyor
        self.btn_clean.configure(text="GEREKSİZ DOSYALARI TEMİZLE (PREFETCH, TEMP, CACHE, LOGS)", fg_color="#313244", text_color="#FAB387")

    def set_timer_max(self):
        try:
            ntdll = ctypes.windll.ntdll
            ntdll.NtSetTimerResolution(5000, 1, ctypes.byref(ctypes.c_ulong()))
            self.lbl_timer.configure(text="DURUM: AKTİF (0.5ms)", text_color="#A6E3A1")
        except:
            self.lbl_timer.configure(text="HATA", text_color="#F38BA8")

    def run_cmd(self, command):
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def start_optimization(self):
        threading.Thread(target=self._optimization_process).start()

    def _optimization_process(self):
        self.btn_apply.configure(text="İŞLEM YAPILIYOR...", state="disabled")
        
        # 1. REGISTRY: Update
        if self.reg_vars["update"].get():
            try:
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU")
                winreg.SetValueEx(key, "NoAutoUpdate", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)
            except: pass

        # 2. REGISTRY: Defender (Lobotomi)
        if self.reg_vars["defender"].get():
            paths = [
                (r"SOFTWARE\Policies\Microsoft\Windows Defender", "DisableAntiSpyware"),
                (r"SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection", "DisableBehaviorMonitoring"),
                (r"SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection", "DisableOnAccessProtection"),
                (r"SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection", "DisableScanOnRealtimeEnable")
            ]
            for path, name in paths:
                try:
                    key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, path)
                    winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, 1)
                    winreg.CloseKey(key)
                except: pass

        # 3. SERVICES: Stop & Disable
        count = 0
        total = 0
        for srv, var in self.service_vars.items():
            if var.get():
                total += 1
                self.run_cmd(f"sc stop {srv}")
                self.run_cmd(f"sc config {srv} start= disabled")
                if total % 10 == 0: time.sleep(0.1)

        self.btn_apply.configure(text=f"TAMAMLANDI - RESET AT", fg_color="#A6E3A1", text_color="#11111B")

# --- AUTO ADMIN ELEVATION (ERİŞİM ENGELİ ÇÖZÜMÜ - DOKUNULMADI) ---
if __name__ == "__main__":
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if is_admin():
        app = KillianOptimizer()
        app.mainloop()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)