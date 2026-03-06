
"""
Configuration multilingue pour TAXRECLAIMAI
Ce module contient toutes les traductions et configurations linguistiques
"""

from typing import Dict, List, Optional
from enum import Enum

class Language(Enum):
    AFRIKAANS = "af"
    ALBANIAN = "sq"
    AMHARIC = "am"
    ARABIC = "ar"
    ARMENIAN = "hy"
    AZERBAIJANI = "az"
    BASQUE = "eu"
    BELARUSIAN = "be"
    BENGALI = "bn"
    BOSNIAN = "bs"
    BULGARIAN = "bg"
    CATALAN = "ca"
    CHINESE_SIMPLIFIED = "zh-CN"
    CHINESE_TRADITIONAL = "zh-TW"
    CROATIAN = "hr"
    CZECH = "cs"
    DANISH = "da"
    DUTCH = "nl"
    ENGLISH = "en"
    ESTONIAN = "et"
    FILIPINO = "tl"
    FINNISH = "fi"
    FRENCH = "fr"
    GALICIAN = "gl"
    GEORGIAN = "ka"
    GERMAN = "de"
    GREEK = "el"
    GUJARATI = "gu"
    HEBREW = "he"
    HINDI = "hi"
    HUNGARIAN = "hu"
    ICELANDIC = "is"
    INDONESIAN = "id"
    IRISH = "ga"
    ITALIAN = "it"
    JAPANESE = "ja"
    KANNADA = "kn"
    KAZAKH = "kk"
    KHMER = "km"
    KOREAN = "ko"
    KYRGYZ = "ky"
    LAO = "lo"
    LATVIAN = "lv"
    LITHUANIAN = "lt"
    MACEDONIAN = "mk"
    MALAY = "ms"
    MALAYALAM = "ml"
    MALTESE = "mt"
    MONGOLIAN = "mn"
    NEPALI = "ne"
    NORWEGIAN = "no"
    PASHTO = "ps"
    PERSIAN = "fa"
    POLISH = "pl"
    PORTUGUESE = "pt"
    PUNJABI = "pa"
    ROMANIAN = "ro"
    RUSSIAN = "ru"
    SERBIAN = "sr"
    SINHALA = "si"
    SLOVAK = "sk"
    SLOVENIAN = "sl"
    SOMALI = "so"
    SPANISH = "es"
    SWAHILI = "sw"
    SWEDISH = "sv"
    TAJIK = "tg"
    TAMIL = "ta"
    TATAR = "tt"
    TELUGU = "te"
    THAI = "th"
    TURKISH = "tr"
    UKRAINIAN = "uk"
    URDU = "ur"
    UZBEK = "uz"
    VIETNAMESE = "vi"
    WELSH = "cy"

# Traductions communes
COMMON_TRANSLATIONS = {
    Language.ENGLISH: {
        "app_name": "TAXRECLAIMAI",
        "dashboard": "Dashboard",
        "documents": "Documents",
        "vat_calculations": "VAT Calculations",
        "forms": "Forms",
        "reports": "Reports",
        "settings": "Settings",
        "logout": "Logout",
        "login": "Login",
        "register": "Register",
        "email": "Email",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "first_name": "First Name",
        "last_name": "Last Name",
        "company_name": "Company Name",
        "phone": "Phone",
        "address": "Address",
        "upload": "Upload",
        "download": "Download",
        "delete": "Delete",
        "edit": "Edit",
        "save": "Save",
        "cancel": "Cancel",
        "submit": "Submit",
        "processing": "Processing",
        "completed": "Completed",
        "failed": "Failed",
        "pending": "Pending",
        "total": "Total",
        "vat_amount": "VAT Amount",
        "recoverable_amount": "Recoverable Amount",
        "vat_rate": "VAT Rate",
        "invoice_date": "Invoice Date",
        "invoice_number": "Invoice Number",
        "supplier": "Supplier",
        "description": "Description",
        "net_amount": "Net Amount",
        "gross_amount": "Gross Amount",
        "currency": "Currency",
        "country": "Country",
        "language": "Language",
        "notifications": "Notifications",
        "profile": "Profile",
        "security": "Security",
        "two_factor_auth": "Two-Factor Authentication",
        "enable_2fa": "Enable 2FA",
        "disable_2fa": "Disable 2FA",
        "backup_codes": "Backup Codes",
        "generate_backup_codes": "Generate Backup Codes",
        "scan_qr_code": "Scan QR Code",
        "enter_code": "Enter Code",
        "verify": "Verify",
        "invalid_code": "Invalid Code",
        "code_expired": "Code Expired",
        "resend_code": "Resend Code",
        "forgot_password": "Forgot Password",
        "reset_password": "Reset Password",
        "new_password": "New Password",
        "confirm_new_password": "Confirm New Password",
        "password_changed": "Password Changed",
        "password_reset_sent": "Password Reset Sent",
        "invalid_credentials": "Invalid Credentials",
        "account_locked": "Account Locked",
        "account_verified": "Account Verified",
        "verification_sent": "Verification Sent",
        "welcome": "Welcome",
        "goodbye": "Goodbye",
        "error_occurred": "An Error Occurred",
        "operation_successful": "Operation Successful",
        "operation_failed": "Operation Failed",
        "no_data_available": "No Data Available",
        "loading": "Loading...",
        "search": "Search",
        "filter": "Filter",
        "sort": "Sort",
        "export": "Export",
        "import": "Import",
        "print": "Print",
        "close": "Close",
        "back": "Back",
        "next": "Next",
        "previous": "Previous",
        "page": "Page",
        "of": "of",
        "items_per_page": "Items per Page",
        "select_all": "Select All",
        "deselect_all": "Deselect All",
        "selected_items": "Selected Items",
        "no_items_selected": "No Items Selected",
        "confirm_delete": "Confirm Delete",
        "are_you_sure": "Are You Sure?",
        "yes": "Yes",
        "no": "No",
        "ok": "OK",
        "help": "Help",
        "about": "About",
        "contact": "Contact",
        "privacy_policy": "Privacy Policy",
        "terms_of_service": "Terms of Service",
        "copyright": "Copyright",
        "all_rights_reserved": "All Rights Reserved",
        "version": "Version",
        "last_updated": "Last Updated"
    },

    Language.FRENCH: {
        "app_name": "TAXRECLAIMAI",
        "dashboard": "Tableau de Bord",
        "documents": "Documents",
        "vat_calculations": "Calculs de TVA",
        "forms": "Formulaires",
        "reports": "Rapports",
        "settings": "Paramètres",
        "logout": "Déconnexion",
        "login": "Connexion",
        "register": "S'inscrire",
        "email": "Email",
        "password": "Mot de Passe",
        "confirm_password": "Confirmer le Mot de Passe",
        "first_name": "Prénom",
        "last_name": "Nom",
        "company_name": "Nom de l'Entreprise",
        "phone": "Téléphone",
        "address": "Adresse",
        "upload": "Télécharger",
        "download": "Télécharger",
        "delete": "Supprimer",
        "edit": "Modifier",
        "save": "Sauvegarder",
        "cancel": "Annuler",
        "submit": "Soumettre",
        "processing": "En Cours",
        "completed": "Terminé",
        "failed": "Échec",
        "pending": "En Attente",
        "total": "Total",
        "vat_amount": "Montant TVA",
        "recoverable_amount": "Montant Recouvrable",
        "vat_rate": "Taux TVA",
        "invoice_date": "Date Facture",
        "invoice_number": "Numéro Facture",
        "supplier": "Fournisseur",
        "description": "Description",
        "net_amount": "Montant Net",
        "gross_amount": "Montant Brut",
        "currency": "Devise",
        "country": "Pays",
        "language": "Langue",
        "notifications": "Notifications",
        "profile": "Profil",
        "security": "Sécurité",
        "two_factor_auth": "Authentification à Deux Facteurs",
        "enable_2fa": "Activer 2FA",
        "disable_2fa": "Désactiver 2FA",
        "backup_codes": "Codes de Sauvegarde",
        "generate_backup_codes": "Générer des Codes de Sauvegarde",
        "scan_qr_code": "Scanner le Code QR",
        "enter_code": "Entrer le Code",
        "verify": "Vérifier",
        "invalid_code": "Code Invalide",
        "code_expired": "Code Expiré",
        "resend_code": "Renvoyer le Code",
        "forgot_password": "Mot de Passe Oublié",
        "reset_password": "Réinitialiser le Mot de Passe",
        "new_password": "Nouveau Mot de Passe",
        "confirm_new_password": "Confirmer le Nouveau Mot de Passe",
        "password_changed": "Mot de Passe Modifié",
        "password_reset_sent": "Réinitialisation Envoyée",
        "invalid_credentials": "Identifiants Invalides",
        "account_locked": "Compte Verrouillé",
        "account_verified": "Compte Vérifié",
        "verification_sent": "Vérification Envoyée",
        "welcome": "Bienvenue",
        "goodbye": "Au Revoir",
        "error_occurred": "Une Erreur est Survenue",
        "operation_successful": "Opération Réussie",
        "operation_failed": "Opération Échouée",
        "no_data_available": "Aucune Donnée Disponible",
        "loading": "Chargement...",
        "search": "Rechercher",
        "filter": "Filtrer",
        "sort": "Trier",
        "export": "Exporter",
        "import": "Importer",
        "print": "Imprimer",
        "close": "Fermer",
        "back": "Retour",
        "next": "Suivant",
        "previous": "Précédent",
        "page": "Page",
        "of": "sur",
        "items_per_page": "Éléments par Page",
        "select_all": "Tout Sélectionner",
        "deselect_all": "Tout Désélectionner",
        "selected_items": "Éléments Sélectionnés",
        "no_items_selected": "Aucun Élément Sélectionné",
        "confirm_delete": "Confirmer la Suppression",
        "are_you_sure": "Êtes-vous Sûr?",
        "yes": "Oui",
        "no": "Non",
        "ok": "OK",
        "help": "Aide",
        "about": "À Propos",
        "contact": "Contact",
        "privacy_policy": "Politique de Confidentialité",
        "terms_of_service": "Conditions d'Utilisation",
        "copyright": "Droit d'Auteur",
        "all_rights_reserved": "Tous Droits Réservés",
        "version": "Version",
        "last_updated": "Dernière Mise à Jour"
    },

    Language.GERMAN: {
        "app_name": "TAXRECLAIMAI",
        "dashboard": "Dashboard",
        "documents": "Dokumente",
        "vat_calculations": "Mehrwertsteuerberechnungen",
        "forms": "Formulare",
        "reports": "Berichte",
        "settings": "Einstellungen",
        "logout": "Abmelden",
        "login": "Anmelden",
        "register": "Registrieren",
        "email": "E-Mail",
        "password": "Passwort",
        "confirm_password": "Passwort Bestätigen",
        "first_name": "Vorname",
        "last_name": "Nachname",
        "company_name": "Firmenname",
        "phone": "Telefon",
        "address": "Adresse",
        "upload": "Hochladen",
        "download": "Herunterladen",
        "delete": "Löschen",
        "edit": "Bearbeiten",
        "save": "Speichern",
        "cancel": "Abbrechen",
        "submit": "Absenden",
        "processing": "In Bearbeitung",
        "completed": "Abgeschlossen",
        "failed": "Fehlgeschlagen",
        "pending": "Ausstehend",
        "total": "Gesamt",
        "vat_amount": "Mehrwertsteuerbetrag",
        "recoverable_amount": "Rückerstattbarer Betrag",
        "vat_rate": "Mehrwertsteuersatz",
        "invoice_date": "Rechnungsdatum",
        "invoice_number": "Rechnungsnummer",
        "supplier": "Lieferant",
        "description": "Beschreibung",
        "net_amount": "Nettobetrag",
        "gross_amount": "Bruttobetrag",
        "currency": "Währung",
        "country": "Land",
        "language": "Sprache",
        "notifications": "Benachrichtigungen",
        "profile": "Profil",
        "security": "Sicherheit",
        "two_factor_auth": "Zwei-Faktor-Authentifizierung",
        "enable_2fa": "2FA Aktivieren",
        "disable_2fa": "2FA Deaktivieren",
        "backup_codes": "Backup-Codes",
        "generate_backup_codes": "Backup-Codes Generieren",
        "scan_qr_code": "QR-Code Scannen",
        "enter_code": "Code Eingeben",
        "verify": "Verifizieren",
        "invalid_code": "Ungültiger Code",
        "code_expired": "Code Abgelaufen",
        "resend_code": "Code Erneut Senden",
        "forgot_password": "Passwort Vergessen",
        "reset_password": "Passwort Zurücksetzen",
        "new_password": "Neues Passwort",
        "confirm_new_password": "Neues Passwort Bestätigen",
        "password_changed": "Passwort Geändert",
        "password_reset_sent": "Passwort-Zurücksetzung Gesendet",
        "invalid_credentials": "Ungültige Anmeldeinformationen",
        "account_locked": "Konto Gesperrt",
        "account_verified": "Konto Verifiziert",
        "verification_sent": "Verifizierung Gesendet",
        "welcome": "Willkommen",
        "goodbye": "Auf Wiedersehen",
        "error_occurred": "Ein Fehler ist Aufgetreten",
        "operation_successful": "Operation Erfolgreich",
        "operation_failed": "Operation Fehlgeschlagen",
        "no_data_available": "Keine Daten Verfügbar",
        "loading": "Laden...",
        "search": "Suchen",
        "filter": "Filtern",
        "sort": "Sortieren",
        "export": "Exportieren",
        "import": "Importieren",
        "print": "Drucken",
        "close": "Schließen",
        "back": "Zurück",
        "next": "Weiter",
        "previous": "Vorherige",
        "page": "Seite",
        "of": "von",
        "items_per_page": "Elemente pro Seite",
        "select_all": "Alle Auswählen",
        "deselect_all": "Alle Abwählen",
        "selected_items": "Ausgewählte Elemente",
        "no_items_selected": "Keine Elemente Ausgewählt",
        "confirm_delete": "Löschen Bestätigen",
        "are_you_sure": "Sind Sie Sicher?",
        "yes": "Ja",
        "no": "Nein",
        "ok": "OK",
        "help": "Hilfe",
        "about": "Über",
        "contact": "Kontakt",
        "privacy_policy": "Datenschutzerklärung",
        "terms_of_service": "Nutzungsbedingungen",
        "copyright": "Urheberrecht",
        "all_rights_reserved": "Alle Rechte Vorbehalten",
        "version": "Version",
        "last_updated": "Zuletzt Aktualisiert"
    },

    Language.SPANISH: {
        "app_name": "TAXRECLAIMAI",
        "dashboard": "Tablero",
        "documents": "Documentos",
        "vat_calculations": "Cálculos de IVA",
        "forms": "Formularios",
        "reports": "Informes",
        "settings": "Configuración",
        "logout": "Cerrar Sesión",
        "login": "Iniciar Sesión",
        "register": "Registrarse",
        "email": "Correo Electrónico",
        "password": "Contraseña",
        "confirm_password": "Confirmar Contraseña",
        "first_name": "Nombre",
        "last_name": "Apellido",
        "company_name": "Nombre de la Empresa",
        "phone": "Teléfono",
        "address": "Dirección",
        "upload": "Subir",
        "download": "Descargar",
        "delete": "Eliminar",
        "edit": "Editar",
        "save": "Guardar",
        "cancel": "Cancelar",
        "submit": "Enviar",
        "processing": "Procesando",
        "completed": "Completado",
        "failed": "Fallido",
        "pending": "Pendiente",
        "total": "Total",
        "vat_amount": "Cantidad de IVA",
        "recoverable_amount": "Cantidad Recuperable",
        "vat_rate": "Tasa de IVA",
        "invoice_date": "Fecha de Factura",
        "invoice_number": "Número de Factura",
        "supplier": "Proveedor",
        "description": "Descripción",
        "net_amount": "Cantidad Neta",
        "gross_amount": "Cantidad Bruta",
        "currency": "Moneda",
        "country": "País",
        "language": "Idioma",
        "notifications": "Notificaciones",
        "profile": "Perfil",
        "security": "Seguridad",
        "two_factor_auth": "Autenticación de Dos Factores",
        "enable_2fa": "Activar 2FA",
        "disable_2fa": "Desactivar 2FA",
        "backup_codes": "Códigos de Respaldo",
        "generate_backup_codes": "Generar Códigos de Respaldo",
        "scan_qr_code": "Escanear Código QR",
        "enter_code": "Ingresar Código",
        "verify": "Verificar",
        "invalid_code": "Código Inválido",
        "code_expired": "Código Expirado",
        "resend_code": "Reenviar Código",
        "forgot_password": "Contraseña Olvidada",
        "reset_password": "Restablecer Contraseña",
        "new_password": "Nueva Contraseña",
        "confirm_new_password": "Confirmar Nueva Contraseña",
        "password_changed": "Contraseña Cambiada",
        "password_reset_sent": "Restablecimiento Enviado",
        "invalid_credentials": "Credenciales Inválidas",
        "account_locked": "Cuenta Bloqueada",
        "account_verified": "Cuenta Verificada",
        "verification_sent": "Verificación Enviada",
        "welcome": "Bienvenido",
        "goodbye": "Adiós",
        "error_occurred": "Ocurrió un Error",
        "operation_successful": "Operación Exitosa",
        "operation_failed": "Operación Fallida",
        "no_data_available": "No Hay Datos Disponibles",
        "loading": "Cargando...",
        "search": "Buscar",
        "filter": "Filtrar",
        "sort": "Ordenar",
        "export": "Exportar",
        "import": "Importar",
        "print": "Imprimir",
        "close": "Cerrar",
        "back": "Atrás",
        "next": "Siguiente",
        "previous": "Anterior",
        "page": "Página",
        "of": "de",
        "items_per_page": "Elementos por Página",
        "select_all": "Seleccionar Todo",
        "deselect_all": "Deseleccionar Todo",
        "selected_items": "Elementos Seleccionados",
        "no_items_selected": "No Hay Elementos Seleccionados",
        "confirm_delete": "Confirmar Eliminación",
        "are_you_sure": "¿Está Seguro?",
        "yes": "Sí",
        "no": "No",
        "ok": "OK",
        "help": "Ayuda",
        "about": "Acerca de",
        "contact": "Contacto",
        "privacy_policy": "Política de Privacidad",
        "terms_of_service": "Términos de Servicio",
        "copyright": "Derechos de Autor",
        "all_rights_reserved": "Todos los Derechos Reservados",
        "version": "Versión",
        "last_updated": "Última Actualización"
    },

    Language.CHINESE_SIMPLIFIED: {
        "app_name": "TAXRECLAIMAI",
        "dashboard": "仪表板",
        "documents": "文档",
        "vat_calculations": "增值税计算",
        "forms": "表格",
        "reports": "报告",
        "settings": "设置",
        "logout": "登出",
        "login": "登录",
        "register": "注册",
        "email": "电子邮件",
        "password": "密码",
        "confirm_password": "确认密码",
        "first_name": "名",
        "last_name": "姓",
        "company_name": "公司名称",
        "phone": "电话",
        "address": "地址",
        "upload": "上传",
        "download": "下载",
        "delete": "删除",
        "edit": "编辑",
        "save": "保存",
        "cancel": "取消",
        "submit": "提交",
        "processing": "处理中",
        "completed": "已完成",
        "failed": "失败",
        "pending": "待处理",
        "total": "总计",
        "vat_amount": "增值税金额",
        "recoverable_amount": "可回收金额",
        "vat_rate": "增值税税率",
        "invoice_date": "发票日期",
        "invoice_number": "发票号码",
        "supplier": "供应商",
        "description": "描述",
        "net_amount": "净额",
        "gross_amount": "总额",
        "currency": "货币",
        "country": "国家",
        "language": "语言",
        "notifications": "通知",
        "profile": "个人资料",
        "security": "安全",
        "two_factor_auth": "双因素认证",
        "enable_2fa": "启用2FA",
        "disable_2fa": "禁用2FA",
        "backup_codes": "备份代码",
        "generate_backup_codes": "生成备份代码",
        "scan_qr_code": "扫描二维码",
        "enter_code": "输入代码",
        "verify": "验证",
        "invalid_code": "无效代码",
        "code_expired": "代码已过期",
        "resend_code": "重新发送代码",
        "forgot_password": "忘记密码",
        "reset_password": "重置密码",
        "new_password": "新密码",
        "confirm_new_password": "确认新密码",
        "password_changed": "密码已更改",
        "password_reset_sent": "密码重置已发送",
        "invalid_credentials": "无效凭据",
        "account_locked": "账户已锁定",
        "account_verified": "账户已验证",
        "verification_sent": "验证已发送",
        "welcome": "欢迎",
        "goodbye": "再见",
        "error_occurred": "发生错误",
        "operation_successful": "操作成功",
        "operation_failed": "操作失败",
        "no_data_available": "无可用数据",
        "loading": "加载中...",
        "search": "搜索",
        "filter": "筛选",
        "sort": "排序",
        "export": "导出",
        "import": "导入",
        "print": "打印",
        "close": "关闭",
        "back": "返回",
        "next": "下一步",
        "previous": "上一步",
        "page": "页",
        "of": "共",
        "items_per_page": "每页项目数",
        "select_all": "全选",
        "deselect_all": "取消全选",
        "selected_items": "已选择项目",
        "no_items_selected": "未选择项目",
        "confirm_delete": "确认删除",
        "are_you_sure": "您确定吗?",
        "yes": "是",
        "no": "否",
        "ok": "确定",
        "help": "帮助",
        "about": "关于",
        "contact": "联系",
        "privacy_policy": "隐私政策",
        "terms_of_service": "服务条款",
        "copyright": "版权",
        "all_rights_reserved": "版权所有",
        "version": "版本",
        "last_updated": "最后更新"
    },

    Language.JAPANESE: {
        "app_name": "TAXRECLAIMAI",
        "dashboard": "ダッシュボード",
        "documents": "ドキュメント",
        "vat_calculations": "消費税計算",
        "forms": "フォーム",
        "reports": "レポート",
        "settings": "設定",
        "logout": "ログアウト",
        "login": "ログイン",
        "register": "登録",
        "email": "メールアドレス",
        "password": "パスワード",
        "confirm_password": "パスワード確認",
        "first_name": "名",
        "last_name": "姓",
        "company_name": "会社名",
        "phone": "電話番号",
        "address": "住所",
        "upload": "アップロード",
        "download": "ダウンロード",
        "delete": "削除",
        "edit": "編集",
        "save": "保存",
        "cancel": "キャンセル",
        "submit": "送信",
        "processing": "処理中",
        "completed": "完了",
        "failed": "失敗",
        "pending": "保留中",
        "total": "合計",
        "vat_amount": "消費税額",
        "recoverable_amount": "回収可能額",
        "vat_rate": "消費税率",
        "invoice_date": "請求書日付",
        "invoice_number": "請求書番号",
        "supplier": "サプライヤー",
        "description": "説明",
        "net_amount": "正味金額",
        "gross_amount": "総額",
        "currency": "通貨",
        "country": "国",
        "language": "言語",
        "notifications": "通知",
        "profile": "プロフィール",
        "security": "セキュリティ",
        "two_factor_auth": "二要素認証",
        "enable_2fa": "2FA有効化",
        "disable_2fa": "2FA無効化",
        "backup_codes": "バックアップコード",
        "generate_backup_codes": "バックアップコード生成",
        "scan_qr_code": "QRコードスキャン",
        "enter_code": "コード入力",
        "verify": "検証",
        "invalid_code": "無効なコード",
        "code_expired": "コード期限切れ",
        "resend_code": "コード再送",
        "forgot_password": "パスワード忘れ",
        "reset_password": "パスワードリセット",
        "new_password": "新しいパスワード",
        "confirm_new_password": "新しいパスワード確認",
        "password_changed": "パスワード変更済み",
        "password_reset_sent": "パスワードリセット送信済み",
        "invalid_credentials": "無効な認証情報",
        "account_locked": "アカウントロック",
        "account_verified": "アカウント認証済み",
        "verification_sent": "認証送信済み",
        "welcome": "ようこそ",
        "goodbye": "さようなら",
        "error_occurred": "エラーが発生しました",
        "operation_successful": "操作成功",
        "operation_failed": "操作失敗",
        "no_data_available": "利用可能なデータなし",
        "loading": "読み込み中...",
        "search": "検索",
        "filter": "フィルター",
        "sort": "ソート",
        "export": "エクスポート",
        "import": "インポート",
        "print": "印刷",
        "close": "閉じる",
        "back": "戻る",
        "next": "次へ",
        "previous": "前へ",
        "page": "ページ",
        "of": "の",
        "items_per_page": "1ページあたりの項目数",
        "select_all": "すべて選択",
        "deselect_all": "すべて選択解除",
        "selected_items": "選択された項目",
        "no_items_selected": "項目が選択されていません",
        "confirm_delete": "削除確認",
        "are_you_sure": "よろしいですか?",
        "yes": "はい",
        "no": "いいえ",
        "ok": "OK",
        "help": "ヘルプ",
        "about": "について",
        "contact": "連絡先",
        "privacy_policy": "プライバシーポリシー",
        "terms_of_service": "利用規約",
        "copyright": "著作権",
        "all_rights_reserved": "すべての権利予約",
        "version": "バージョン",
        "last_updated": "最終更新"
    }
}

# Configuration des pays par langue
COUNTRY_LANGUAGE_MAPPING = {
    Language.ENGLISH: [
        "US", "GB", "AU", "CA", "IE", "NZ", "ZA", "IN", "PH", "SG", "MY", "HK", "NG", "KE", "GH", "UG", "TZ", "ZW", "BW", "MW", "ZM", "SZ", "LS", "NA", "MW", "MG", "MU", "SC", "KM", "CV", "GW", "ST", "AO", "MZ", "BI", "RW", "DJ", "SO", "ET", "ER", "SD", "LY", "EG", "TN", "DZ", "MA", "EH", "MR", "ML", "NE", "BF", "CI", "LR", "SL", "GN", "GW", "SN", "GM", "GN-B", "CV", "ST", "AO", "MZ", "BI", "RW", "DJ", "SO", "ET", "ER", "SD", "LY", "EG", "TN", "DZ", "MA", "EH", "MR", "ML", "NE", "BF", "CI", "LR", "SL", "GN", "GW", "SN", "GM", "GN-B"
    ],
    Language.FRENCH: [
        "FR", "BE", "LU", "CH", "MC", "AD", "CA", "CD", "CG", "CI", "GA", "GN", "HT", "LU", "MC", "ML", "NE", "SN", "TD", "TG", "BF", "BI", "CM", "CF", "DJ", "GQ", "KM", "MG", "MA", "NC", "PF", "RE", "RW", "SC", "SY", "TD", "TG", "VU", "WF", "YT"
    ],
    Language.GERMAN: [
        "DE", "AT", "CH", "LI", "LU", "BE"
    ],
    Language.SPANISH: [
        "ES", "MX", "AR", "CO", "PE", "VE", "CL", "EC", "GT", "CU", "BO", "DO", "HN", "PY", "SV", "NI", "CR", "PA", "UY", "GQ", "PR"
    ],
    Language.CHINESE_SIMPLIFIED: [
        "CN", "SG", "MY", "ID", "PH", "TH", "VN", "KH", "LA", "MM", "BN", "TL"
    ],
    Language.JAPANESE: [
        "JP"
    ]
}

# Configuration des formats de date et de nombre par langue
DATE_NUMBER_FORMATS = {
    Language.ENGLISH: {
        "date_format": "MM/DD/YYYY",
        "time_format": "12h",
        "decimal_separator": ".",
        "thousands_separator": ","
    },
    Language.FRENCH: {
        "date_format": "DD/MM/YYYY",
        "time_format": "24h",
        "decimal_separator": ",",
        "thousands_separator": " "
    },
    Language.GERMAN: {
        "date_format": "DD.MM.YYYY",
        "time_format": "24h",
        "decimal_separator": ",",
        "thousands_separator": "."
    },
    Language.SPANISH: {
        "date_format": "DD/MM/YYYY",
        "time_format": "24h",
        "decimal_separator": ",",
        "thousands_separator": "."
    },
    Language.CHINESE_SIMPLIFIED: {
        "date_format": "YYYY-MM-DD",
        "time_format": "24h",
        "decimal_separator": ".",
        "thousands_separator": ","
    },
    Language.JAPANESE: {
        "date_format": "YYYY/MM/DD",
        "time_format": "24h",
        "decimal_separator": ".",
        "thousands_separator": ","
    }
}

# Fonctions utilitaires pour les traductions
def get_translation(language: Language, key: str) -> str:
    """
    Récupère une traduction pour une langue et une clé spécifiques

    Args:
        language: Langue cible
        key: Clé de traduction

    Returns:
        str: Traduction ou clé si non trouvée
    """
    if language in COMMON_TRANSLATIONS and key in COMMON_TRANSLATIONS[language]:
        return COMMON_TRANSLATIONS[language][key]
    return key

def get_language_for_country(country_code: str) -> Language:
    """
    Détermine la langue principale pour un pays

    Args:
        country_code: Code ISO du pays

    Returns:
        Language: Langue principale du pays
    """
    for language, countries in COUNTRY_LANGUAGE_MAPPING.items():
        if country_code in countries:
            return language
    return Language.ENGLISH  # Langue par défaut

def get_date_number_format(language: Language) -> Dict[str, str]:
    """
    Récupère les formats de date et de nombre pour une langue

    Args:
        language: Langue cible

    Returns:
        Dict[str, str]: Formats de date et de nombre
    """
    return DATE_NUMBER_FORMATS.get(language, DATE_NUMBER_FORMATS[Language.ENGLISH])
