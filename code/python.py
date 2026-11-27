import ast
import json
import os
import re
import threading
import time
import traceback
from collections import deque
from typing import Any, List

from android.os import Bundle
from java.util import Locale

try:
    from org.telegram.messenger import FileLoader, NotificationCenter
except Exception:
    from org.telegram.messenger import FileLoader
    NotificationCenter = None

from org.telegram.tgnet import TLRPC
from org.telegram.ui import ChatActivity

from android_utils import log, run_on_ui_thread

try:
    from android_utils import OnClickListener
except Exception:
    OnClickListener = None

from base_plugin import BasePlugin

try:
    from hook_utils import find_class
except Exception:
    find_class = None

try:
    from android.view import View
except Exception:
    View = None

try:
    from android.animation import ValueAnimator
except Exception:
    ValueAnimator = None

try:
    from android.graphics.drawable import GradientDrawable, InsetDrawable
except Exception:
    GradientDrawable = None
    try:
        from android.graphics.drawable import InsetDrawable
    except Exception:
        InsetDrawable = None
from client_utils import (
    PLUGINS_QUEUE,
    RequestCallback,
    get_file_loader,
    get_last_fragment,
    get_messages_controller,
    run_on_queue,
    send_request,
)
try:
    if RequestCallback is not None and not hasattr(RequestCallback, "__call__"):
        RequestCallback.__call__ = lambda self, response, error: self.run(response, error)
except Exception:
    pass
from file_utils import get_plugins_dir, list_dir
from ui.alert import AlertDialogBuilder
from ui.bulletin import BulletinHelper
from ui.settings import Divider, Header, Switch, Text

WORK_QUEUE = PLUGINS_QUEUE

try:
    from client_utils import get_connections_manager
except Exception:
    get_connections_manager = None

try:
    from client_utils import get_notification_center
except Exception:
    get_notification_center = None

try:
    from org.telegram.messenger import AndroidUtilities
except Exception:
    AndroidUtilities = None

try:
    from org.telegram.ui.ActionBar import Theme
except Exception:
    Theme = None

try:
    from file_utils import get_cache_dir
except Exception:
    get_cache_dir = None

try:
    from java import dynamic_proxy, jclass
except Exception:
    dynamic_proxy = None
    jclass = None

__id__ = "plugin_update_checker"
__name__ = "Plugin Update Checker"
__description__ = "Checking for updates for your installed plugins from multiple channels."
__author__ = "@itNotMax - @MaxExteraPlugins"
__version__ = "3.3.9"
__icon__ = "MaxExteraPluginsStickers/24"
__min_version__ = "12.10.6"
__app_version__ = ">=12.5.1"
__sdk_version__ = ">=1.4.3.3"

STRINGS = {
    "en": {
        "plugin_name": "Plugin Update Checker",
        "check_button": "Check for updates",
        "auto_check": "Check on startup",
        "auto_check_sub": "Silently check when app starts, notify only if updates found",
        "channels_header": "Channels",
        "channels_hint": "Channels separated by spaces",
        "channels_edit": "Change channels",
        "save": "Save",
        "channels_saved": "Channels saved",
        "minimize": "Minimize",
        "minimized_info": "The check continues in the background",
        "show_badge": "Update icon in top bar",
        "show_badge_sub": "Show an icon in the top bar when plugin updates are available",
        "history_header": "History",
        "open_results": "Open last scan results",
        "no_scan": "No scan performed yet",
        "updates_available": "{} update(s) available",
        "all_up_to_date": "All plugins up to date",
        "no_plugins": "No installed plugins found.",
        "no_channels": "No channels configured.",
"checking_title": "Checking for updates",
        "waiting_connection": "Waiting for connection...",
        "reading_plugins": "Reading installed plugins...",
        "found_plugins": "Found {} plugins. Checking {} channel(s)...",
        "resolving_channel": "Resolving @{}... ({}/{})",
"searching_channel": "Searching files in @{}...",
        "searching_page": "Searching @{}... (page {})",
        "deep_scan_phase": "Scanning history for missing plugins...",
        "deep_scan_channel": "Deep scanning @{}... ({}/{})",
        "deep_scan_page": "Deep scan @{}... (page {})",
        "downloading_files": "Downloading {} file(s)...",
        "downloading_progress": "Downloading {}/{} files...",
        "comparing_versions": "Comparing versions...",
        "done": "Done!",
        "error_comparing": "Error comparing versions",
        "results_title": "Update Check Results",
        "updates_header": "\U0001f504 Updates available ({}):",
        "update_line": "  \u2022 {}",
        "version_line": "    {} \u2192 {}  (@{})",
        "up_to_date_header": "\u2705 Up to date: {} plugin(s)",
        "not_found_header": "\u2753 Not in channels ({}):",
        "not_found_item": "  \u2022 {}",
        "channel_errors_header": "\u26a0\ufe0f Channel errors:",
        "channel_error_item": "  \u26a0\ufe0f @{}: {}",
        "open_in_channel": "Open in channel",
        "close": "Close",
        "ok": "OK",
        "back": "Back",
        "open_plugin_in_channel": "Open plugin in channel",
        "failed_open": "Failed to open message",
        "check_complete": "Check complete",
        "no_plugins_to_check": "No plugins to check.",
        "cancel": "Cancel",
        "check_cancelled": "Check cancelled",
        "tab_updates": "Updates",
        "tab_not_found": "Not found",
        "tab_up_to_date": "Up to date",
        "not_found_hint": "Not found in channels",
        "tab_updates_desc": "Updates are available for these plugins:",
        "tab_updates_empty": "No updates available",
        "tab_not_found_desc": "These plugins were not found in the configured channels. If you know a trusted channel that has one, add it to the plugin settings.",
        "tab_not_found_empty": "All plugins were found in the configured channels",
        "tab_up_to_date_desc": "These plugins are on the latest version:",
        "tab_up_to_date_empty": "All plugins are up to date",
        "ignored_header": "Ignored updates",
        "ignored_manage": "Manage ignored plugins",
        "ignored_none": "No ignored plugins",
        "ignored_summary": "{} plugin(s) ignored",
        "ignored_add": "Add ignored plugin",
        "ignored_hint_id": "Plugin id",
        "ignored_hint_version": "Version (empty = all versions)",
        "ignored_all_label": "all versions",
        "ignored_versions_label": "versions: {}",
        "ignored_empty_list": "Nothing is ignored yet",
        "ignored_saved": "Ignore list updated",
        "ignored_need_id": "Plugin id is required",
        "ignored_title": "Ignored plugins",
        "ignored_pick_title": "Choose plugin",
        "ignored_pick_hint": "Select an installed plugin:",
        "ignored_no_plugins": "No installed plugins found",
        "channels_pick_title": "Select channels",
        "channels_pick_hint": "Your public channels and groups. Tap to toggle.",
        "channels_pick_selected": "Selected: {}",
        "channels_pick_manual": "Enter manually",
        "channels_none_available": "No public channels found among your chats. Use manual input.",
        "channels_choose_method": "Choose how to configure channels:",
        "channels_open_tg_picker": "Open TG picker",
        "channels_enter_username": "Enter @username",
        "channels_no_username_selected": "Selected chats have no public @username",
        "version_same_line": "{}  \u2192  {}",
        "channel_suffix": "@{}",
        "ignore_question": "Are you sure you want to ignore this update?",
        "ignore_all_versions": "Ignore all versions of this plugin",
        "ignore_this_version": "Ignore only this version",
        "ignored_bulletin": "Update ignored",
    },
    "ru": {
        "plugin_name": "Проверка обновлений плагинов",
        "check_button": "Проверить обновления",
        "auto_check": "Проверять при запуске",
        "auto_check_sub": "Тихо проверять при запуске приложения, уведомлять только если есть обновления",
        "channels_header": "Каналы",
        "channels_hint": "Каналы через пробел",
        "channels_edit": "Изменить каналы",
        "save": "Сохранить",
        "channels_saved": "Каналы сохранены",
        "minimize": "Свернуть",
        "minimized_info": "Проверка продолжится в фоне",
        "show_badge": "Значок обновлений на панели",
        "show_badge_sub": "Показывать значок на верхней панели, когда есть обновления плагинов",
        "history_header": "История",
        "open_results": "Открыть результаты последней проверки",
        "no_scan": "Проверок ещё не было",
        "updates_available": "Доступно обновлений: {}",
        "all_up_to_date": "Все плагины актуальны",
        "no_plugins": "Установленных плагинов не найдено.",
        "no_channels": "Каналы не настроены.",
"checking_title": "Проверка обновлений",
        "waiting_connection": "Ожидание соединения...",
        "reading_plugins": "Чтение установленных плагинов...",
        "found_plugins": "Найдено {} плагинов. Проверка {} каналов...",
        "resolving_channel": "Разрешение @{}... ({}/{})",
"searching_channel": "Поиск файлов в @{}...",
        "searching_page": "Поиск в @{}... (страница {})",
        "deep_scan_phase": "Сканирование истории для ненайденных плагинов...",
        "deep_scan_channel": "Глубокое сканирование @{}... ({}/{})",
        "deep_scan_page": "Глубокий поиск в @{}... (страница {})",
        "downloading_files": "Загрузка {} файлов...",
        "downloading_progress": "Загружено {}/{} файлов...",
        "comparing_versions": "Сравнение версий...",
        "done": "Готово!",
        "error_comparing": "Ошибка при сравнении версий",
        "results_title": "Результаты проверки",
        "updates_header": "\U0001f504 Доступны обновления ({}):",
        "update_line": "  \u2022 {}",
        "version_line": "    {} \u2192 {}  (@{})",
        "up_to_date_header": "\u2705 Актуальны: {} плагинов",
        "not_found_header": "\u2753 Не найдены в каналах ({}):",
        "not_found_item": "  \u2022 {}",
        "channel_errors_header": "\u26a0\ufe0f Ошибки каналов:",
        "channel_error_item": "  \u26a0\ufe0f @{}: {}",
        "open_in_channel": "Открыть в канале",
        "close": "Закрыть",
        "ok": "ОК",
        "back": "Назад",
        "open_plugin_in_channel": "Открыть плагин в канале",
        "failed_open": "Не удалось открыть сообщение",
        "check_complete": "Проверка завершена",
        "no_plugins_to_check": "Нет плагинов для проверки.",
        "cancel": "Отмена",
        "check_cancelled": "Проверка отменена",
        "tab_updates": "Обновления",
        "tab_not_found": "Не найдены",
        "tab_up_to_date": "Актуальные",
        "not_found_hint": "Не найден в каналах",
        "tab_updates_desc": "Для этих плагинов доступны обновления:",
        "tab_updates_empty": "Доступных обновлений нет",
        "tab_not_found_desc": "Эти плагины не найдены в подключённых каналах. Если знаете канал, где есть такой плагин — добавьте его в настройки проверки (только если доверяете источнику).",
        "tab_not_found_empty": "Все плагины найдены в подключённых каналах",
        "tab_up_to_date_desc": "Эти плагины уже на актуальной версии:",
        "tab_up_to_date_empty": "Все плагины актуальны",
        "ignored_header": "Игнорируемые обновления",
        "ignored_manage": "Управление игнорируемыми",
        "ignored_none": "Нет игнорируемых плагинов",
        "ignored_summary": "Игнорируется плагинов: {}",
        "ignored_add": "Добавить игнорирование",
        "ignored_hint_id": "ID плагина",
        "ignored_hint_version": "Версия (пусто = все версии)",
        "ignored_all_label": "все версии",
        "ignored_versions_label": "версии: {}",
        "ignored_empty_list": "Список пуст",
        "ignored_saved": "Список игнорирования обновлён",
        "ignored_need_id": "Укажите ID плагина",
        "ignored_title": "Игнорируемые плагины",
        "ignored_pick_title": "Выберите плагин",
        "ignored_pick_hint": "Выберите установленный плагин:",
        "ignored_no_plugins": "Установленные плагины не найдены",
        "channels_pick_title": "Выбор каналов",
        "channels_pick_hint": "Ваши публичные каналы и группы. Нажмите, чтобы выбрать.",
        "channels_pick_selected": "Выбрано: {}",
        "channels_pick_manual": "Ввести вручную",
        "channels_none_available": "Среди ваших чатов нет публичных каналов. Используйте ручной ввод.",
        "channels_choose_method": "Выберите способ настройки каналов:",
        "channels_open_tg_picker": "Открыть TG пикер",
        "channels_enter_username": "Указать @username",
        "channels_no_username_selected": "У выбранных чатов нет публичного @username",
        "version_same_line": "{}  \u2192  {}",
        "channel_suffix": "@{}",
        "ignore_question": "Уверены, что хотите игнорировать данное обновление?",
        "ignore_all_versions": "Игнорировать все версии данного плагина",
        "ignore_this_version": "Игнорировать только эту версию",
        "ignored_bulletin": "Обновление игнорируется",
    }
}

DEFAULT_CHANNELS_TEXT = "@exteraPluginsSup @PESSDES_Plugins @RnPlugins @swagnonher @ytilities @MaxExteraPlugins"

CACHE_FILE_NAME = "plugin_update_checker_cache.json"
CACHE_VERSION = 2

HISTORY_PAGE_LIMIT = 100
MAX_HISTORY_PAGES = 200
MAX_DEEP_SCAN_PAGES = 200

POLL_INTERVAL_MS = 300
FILES_PER_POLL = 8
MAX_CONCURRENT_DOWNLOADS = 3
MAX_DOWNLOAD_ATTEMPTS = 75
RELOAD_EVERY_ATTEMPTS = 20

CONNECTION_POLL_MS = 2000
CONNECTION_WAIT_TIMEOUT_S = 45.0

PROGRESS_THROTTLE_MS = 330.0

PROGRESS_SEARCH_BASE = 5
PROGRESS_SEARCH_SPAN = 28
PROGRESS_DL1_BASE = 35
PROGRESS_DL1_SPAN = 30
PROGRESS_DEEP_INTRO = 66
PROGRESS_DEEP_BASE = 67
PROGRESS_DEEP_SPAN = 18
PROGRESS_DL2_BASE = 85
PROGRESS_DL2_SPAN = 12
PROGRESS_FINALIZE = 98

AUTO_CHECK_DELAY_MS = 15000
AUTO_CHECK_MIN_INTERVAL_S = 30 * 60.0
DEEP_SCAN_MIN_INTERVAL_S = 3 * 24 * 3600.0
FULL_SCAN_MIN_INTERVAL_S = 3 * 24 * 3600.0
INCREMENTAL_SLACK_S = 24 * 3600

ONLINE_CONNECTION_STATES = (3, 5)


if dynamic_proxy is not None and NotificationCenter is not None:

    class _ConnectionStateDelegate(dynamic_proxy(NotificationCenter.NotificationCenterDelegate)):

        def __init__(self, plugin):
            self._plugin = plugin

        def didReceivedNotification(self, nid, account, args):
            try:
                plugin = self._plugin
                if plugin is not None:
                    plugin._on_connection_state()
            except Exception:
                pass


    class _PluginsUpdatedDelegate(dynamic_proxy(NotificationCenter.NotificationCenterDelegate)):

        def __init__(self, plugin):
            self._plugin = plugin

        def didReceivedNotification(self, nid, account, args):
            try:
                plugin = self._plugin
                if plugin is not None:
                    plugin._on_plugins_updated_notification()
            except Exception:
                pass

else:

    _ConnectionStateDelegate = None
    _PluginsUpdatedDelegate = None


def entry_name(file_path):
    try:
        return os.path.basename(str(file_path))
    except Exception:
        return str(file_path)


PUC_BUTTON_ID = 231
PULSE_MAX_ALPHA = 0x3C
PULSE_DURATION_MS = 1200


if dynamic_proxy is not None and ValueAnimator is not None:

    class _PulseUpdateListener(dynamic_proxy(ValueAnimator.AnimatorUpdateListener)):

        def __init__(self, plugin, item, drawable):
            super().__init__()
            self._plugin = plugin
            self._item = item
            self._drawable = drawable

        def onAnimationUpdate(self, animator):
            try:
                v = float(animator.getAnimatedValue())
                alpha = int(PULSE_MAX_ALPHA * v)
                color = (alpha << 24) | 0x00FF3B30
                if self._drawable is not None:
                    self._drawable.setColor(color)
                else:
                    self._item.setBackgroundColor(color)
            except Exception:
                pass

else:

    _PulseUpdateListener = None


class _DialogsCreateViewHook:
    def __init__(self, plugin):
        self.plugin = plugin

    def after_hooked_method(self, param):
        try:
            fragment = param.thisObject
            if not self.plugin._is_main_dialogs_screen(fragment):
                return
            self.plugin._injected_btn = None
            run_on_ui_thread(lambda: self.plugin._add_icon_to_fragment(fragment), 300)
            if self.plugin._updates:
                run_on_queue(self.plugin._reconcile_stored_updates, WORK_QUEUE, 350)
        except Exception:
            pass


class _DialogsResumeHook:
    def __init__(self, plugin):
        self.plugin = plugin

    def after_hooked_method(self, param):
        try:
            fragment = param.thisObject
            if not self.plugin._is_main_dialogs_screen(fragment):
                return
            self.plugin._add_icon_to_fragment(fragment)
            if self.plugin._updates:
                run_on_queue(self.plugin._reconcile_stored_updates, WORK_QUEUE, 100)
        except Exception:
            pass


class _DialogsVisibleHook:
    def __init__(self, plugin):
        self.plugin = plugin

    def after_hooked_method(self, param):
        try:
            fragment = param.thisObject
            if not self.plugin._is_main_dialogs_screen(fragment):
                return
            run_on_ui_thread(lambda: self.plugin._add_icon_to_fragment(fragment), 200)
            if self.plugin._updates:
                run_on_queue(self.plugin._reconcile_stored_updates, WORK_QUEUE, 250)
        except Exception:
            pass



# ============================================================
# MaxExteraPlugins Shared Author & Channel Subscription Module
# ============================================================

# ============================================================
# MaxExteraPlugins Shared Author & Channel Subscription Module
# ============================================================

# ============================================================
# MaxExteraPlugins Shared Author & Channel Subscription Module
# ============================================================
class AuthorChannelHelper:
    CONFIG_URL = "https://raw.githubusercontent.com/MaxExteraPlugins/config/main/links.json"

    DEFAULT_LINKS = {
        "channel_username": "MaxExteraPlugins",
        "channel_url": "https://t.me/MaxExteraPlugins",
        "header": {"ru": "MaxExteraPlugins", "en": "MaxExteraPlugins"},
        "buttons": [
            {"title": {"ru": "Канал автора", "en": "Author's Channel"}, "icon": "msg_channel", "url": "https://t.me/MaxExteraPlugins"},
            {"title": {"ru": "Поддержать автора", "en": "Support author"}, "icon": "msg_share", "url": "https://t.me/itNotMax"},
            {"title": {"ru": "Сообщить о баге", "en": "Report a bug"}, "icon": "msg_help", "url": "https://t.me/itNotMax"}
        ]
    }

    _TEXTS = {
        "install_card_title": {"ru": "Подпишитесь на канал", "en": "Subscribe to channel"},
        "install_card_msg": {
            "ru": (
                "Мы делаем плагины бесплатными и доступными для всех: пожалуйста, "
                "поддержите нас подпиской на официальный канал @MaxExteraPlugins.\n\n"
                "Там публикуются обновления, важные новости и анонсы новых плагинов."
            ),
            "en": (
                "We keep our plugins free and accessible for everyone: please "
                "support us by subscribing to our official channel @MaxExteraPlugins.\n\n"
                "Updates, news, and new plugin announcements are published there."
            )
        },
        "open_channel_btn": {"ru": "Перейти на канал", "en": "Open channel"},
        "remind_later_btn": {"ru": "Напомнить позже", "en": "Remind later"},
        "never_show_btn": {"ru": "Больше не показывать", "en": "Don't show again"},
        "sub_thank_you": {"ru": "Спасибо за подписку на наш канал!", "en": "Thank you for subscribing to our channel!"},
        "settings_channel": {"ru": "Канал автора", "en": "Author's Channel"},
        "settings_donate": {"ru": "Поддержать автора", "en": "Support author"},
        "settings_bug_report": {"ru": "Сообщить о баге", "en": "Report a bug"}
    }

    @classmethod
    def is_ru(cls) -> bool:
        try:
            from org.telegram.messenger import LocaleController
            lang = str(LocaleController.getInstance().getCurrentLocale().getLanguage() or "").lower()
            return lang in ("ru", "be", "uk", "kk")
        except Exception:
            return True

    @classmethod
    def tr(cls, key: str) -> str:
        entry = cls._TEXTS.get(key, {})
        return entry.get("ru" if cls.is_ru() else "en", entry.get("en", key))

    def __init__(self, plugin, icon_sticker=None):
        self.plugin = plugin
        self.icon_sticker = icon_sticker or getattr(plugin, "__icon__", "MaxExteraPluginsStickers/1")
        self._stopped = False
        self._active_dialog = None

    def on_load(self):
        self._stopped = False
        self._active_dialog = None
        self._load_remote_links_async()
        self._check_initial_subscription_flow()

    def on_event(self, event_type):
        try:
            name = str(event_type).upper()
            if name.endswith("START") or name.endswith("RESUME"):
                if self.is_subscribed() and not self.plugin.get_setting("was_subscribed", False):
                    self.plugin.set_setting("was_subscribed", True)
                    self._dismiss_active_dialog()
                    self._notify_subscribed()
        except Exception:
            pass

    def on_unload(self):
        self._stopped = True
        self._dismiss_active_dialog()

    def is_allowed(self) -> bool:
        return True

    def _get_links(self) -> dict:
        raw = self.plugin.get_setting("remote_links_cache", None)
        if raw:
            try:
                import json
                data = json.loads(raw)
                if isinstance(data, dict): return data
            except Exception:
                pass
        return self.DEFAULT_LINKS

    def _load_remote_links_async(self):
        def worker():
            try:
                import urllib.request, json
                req = urllib.request.Request(self.CONFIG_URL, headers={"User-Agent": "MaxExteraPlugins"})
                with urllib.request.urlopen(req, timeout=4) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        if isinstance(data, dict):
                            self.plugin.set_setting("remote_links_cache", json.dumps(data))
                            self._resolve_channel_in_telegram(data.get("channel_username", "MaxExteraPlugins"))
            except Exception:
                pass
        import threading
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _open_url(self, url: str, view=None):
        try:
            from org.telegram.messenger.browser import Browser
            from org.telegram.messenger import ApplicationLoader
            from client_utils import get_last_fragment
            ctx = None
            if view is not None:
                ctx = view.getContext()
            if ctx is None:
                frag = get_last_fragment()
                if frag is not None:
                    ctx = frag.getParentActivity()
            if ctx is None:
                ctx = ApplicationLoader.applicationContext
            Browser.openUrl(ctx, url)
        except Exception:
            pass

    def _resolve_channel_in_telegram(self, username: str):
        try:
            from org.telegram.messenger import UserConfig, MessagesController
            from org.telegram.tgnet import TLRPC, ConnectionsManager, RequestDelegate
            clean_user = username.lstrip("@")
            acc = int(UserConfig.selectedAccount)
            mc = MessagesController.getInstance(acc)
            if not mc: return
            req = TLRPC.TL_contacts_resolveUsername()
            req.username = clean_user
            helper_ref = self
            class Delegate(RequestDelegate):
                def run(self, response, error):
                    if error is None and response is not None:
                        chats = getattr(response, "chats", None)
                        if chats is not None and chats.size() > 0:
                            for a in range(UserConfig.MAX_ACCOUNT_COUNT):
                                try:
                                    if UserConfig.getInstance(a).isClientActivated():
                                        MessagesController.getInstance(a).putChats(chats, False)
                                except Exception:
                                    pass
                            c = chats.get(0)
                            cid = getattr(c, "id", 0)
                            if cid > 0:
                                helper_ref.plugin.set_setting("resolved_channel_id", int(cid))
            ConnectionsManager.getInstance(acc).sendRequest(req, Delegate())
        except Exception:
            pass

    def is_subscribed(self) -> bool:
        try:
            from org.telegram.messenger import UserConfig, MessagesController, MessagesStorage
            from java.lang import Long as JLong
            links = self._get_links()
            target = str(links.get("channel_username", "MaxExteraPlugins") or "MaxExteraPlugins").lower().lstrip("@")
            saved_cid = int(self.plugin.get_setting("resolved_channel_id", 0) or 0)

            for acc in range(UserConfig.MAX_ACCOUNT_COUNT):
                try:
                    uconf = UserConfig.getInstance(acc)
                    if not uconf.isClientActivated():
                        continue

                    mc = MessagesController.getInstance(acc)
                    storage = MessagesStorage.getInstance(acc)

                    # 1. In-memory check by resolved_channel_id
                    if saved_cid and mc is not None:
                        try:
                            c = mc.getChat(JLong(saved_cid))
                            if c is not None:
                                left = bool(getattr(c, "left", True))
                                kicked = bool(getattr(c, "kicked", False))
                                if not left and not kicked:
                                    return True
                        except Exception:
                            pass

                    # 2. In-memory check by username
                    if mc is not None:
                        try:
                            chat = mc.getUserOrChat(target)
                            if chat is not None:
                                cid = int(getattr(chat, "id", 0) or 0)
                                if cid and not saved_cid:
                                    saved_cid = cid
                                    self.plugin.set_setting("resolved_channel_id", cid)
                                left = bool(getattr(chat, "left", True))
                                kicked = bool(getattr(chat, "kicked", False))
                                if not left and not kicked:
                                    return True
                        except Exception:
                            pass

                    # 3. In-memory dialogs check
                    if mc is not None:
                        try:
                            dialog_lists = []
                            d_chan = getattr(mc, "dialogsChannelsOnly", None)
                            if d_chan is not None and d_chan.size() > 0:
                                dialog_lists.append(d_chan)
                            d_all = getattr(mc, "allDialogs", None)
                            if d_all is not None and d_all.size() > 0:
                                dialog_lists.append(d_all)

                            for d_list in dialog_lists:
                                limit = min(d_list.size(), 300)
                                for i in range(limit):
                                    d = d_list.get(i)
                                    did = getattr(d, "id", 0)
                                    if did < 0:
                                        cid = -did
                                        if saved_cid and cid == saved_cid:
                                            c = mc.getChat(JLong(cid))
                                            if c is not None:
                                                left = bool(getattr(c, "left", True))
                                                kicked = bool(getattr(c, "kicked", False))
                                                if not left and not kicked:
                                                    return True
                                        else:
                                            c = mc.getChat(JLong(cid))
                                            if c is not None:
                                                uname = str(getattr(c, "username", "") or "").lower()
                                                if uname == target:
                                                    if not saved_cid:
                                                        saved_cid = cid
                                                        self.plugin.set_setting("resolved_channel_id", cid)
                                                    left = bool(getattr(c, "left", True))
                                                    kicked = bool(getattr(c, "kicked", False))
                                                    if not left and not kicked:
                                                        return True
                        except Exception:
                            pass

                    # 4. Storage check (SQLite on disk)
                    if storage is not None:
                        if saved_cid:
                            try:
                                if storage.containsLocalDialog(JLong(-saved_cid)):
                                    c_sync = storage.getChatSync(JLong(saved_cid))
                                    if c_sync is not None:
                                        left = bool(getattr(c_sync, "left", True))
                                        kicked = bool(getattr(c_sync, "kicked", False))
                                        if not left and not kicked:
                                            return True
                                    else:
                                        return True
                            except Exception:
                                pass

                        try:
                            db = storage.getDatabase()
                            if db is not None:
                                if saved_cid:
                                    try:
                                        cur = db.queryFinalized("SELECT did FROM dialogs WHERE did = ?", [JLong(-saved_cid)])
                                        if cur is not None:
                                            has_row = bool(cur.next())
                                            cur.dispose()
                                            if has_row:
                                                return True
                                    except Exception:
                                        pass

                                try:
                                    cur = db.queryFinalized("SELECT uid, name FROM chats WHERE LOWER(name) LIKE ?", ["%" + target + "%"])
                                    if cur is not None:
                                        while cur.next():
                                            c_id = cur.longValue(0)
                                            if c_id > 0:
                                                if not saved_cid:
                                                    saved_cid = int(c_id)
                                                    self.plugin.set_setting("resolved_channel_id", saved_cid)
                                                cur_d = db.queryFinalized("SELECT did FROM dialogs WHERE did = ?", [JLong(-c_id)])
                                                if cur_d is not None:
                                                    in_dlg = bool(cur_d.next())
                                                    cur_d.dispose()
                                                    if in_dlg:
                                                        cur.dispose()
                                                        return True
                                        cur.dispose()
                                except Exception:
                                    pass
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass
        return False

    def prepend_settings(self, original_items=None) -> list:
        from ui.settings import Header, Text, Divider

        if original_items and any(getattr(x, "text", "") == "MaxExteraPlugins" for x in original_items if type(x).__name__ == "Header"):
            return original_items

        links = self._get_links()
        buttons_config = links.get("buttons")

        author_items = []
        if isinstance(buttons_config, list):
            for btn in buttons_config:
                if not isinstance(btn, dict): continue
                raw_url = btn.get("url")
                if isinstance(raw_url, dict):
                    keys = [
                        getattr(self.plugin, "id", None),
                        globals().get("__id__", None),
                        globals().get("__name__", None),
                        self.plugin.__class__.__name__
                    ]
                    keys += [k.lower() for k in keys if isinstance(k, str)]
                    resolved_url = ""
                    for k in keys:
                        if k and k in raw_url:
                            resolved_url = str(raw_url[k] or "").strip()
                            if resolved_url:
                                break
                    url = resolved_url
                elif isinstance(raw_url, str):
                    url = raw_url.strip()
                else:
                    url = ""

                if not url: continue

                title_data = btn.get("title")
                if isinstance(title_data, dict):
                    title = title_data.get("ru" if self.is_ru() else "en") or title_data.get("en") or title_data.get("ru") or ""
                elif isinstance(title_data, str) and title_data:
                    title = title_data
                else:
                    title = btn.get("title_ru" if self.is_ru() else "title_en") or btn.get("title_ru") or btn.get("title_en") or ""

                if not title: continue
                icon = str(btn.get("icon") or "msg_channel").strip()

                def make_click(u):
                    return lambda v=None: self._open_url(u, v)

                author_items.append(Text(text=title, icon=icon, on_click=make_click(url)))
        else:
            for k, text_key, icon_name in [
                ("channel_url", "settings_channel", "msg_channel"),
                ("donate_url", "settings_donate", "msg_share"),
                ("bug_report_url", "settings_bug_report", "msg_help")
            ]:
                u = str(links.get(k) or "").strip()
                if u:
                    author_items.append(Text(text=self.tr(text_key), icon=icon_name, on_click=lambda v=None, target_u=u: self._open_url(target_u, v)))

        res = []
        if author_items:
            hdr = links.get("header") or "MaxExteraPlugins"
            if isinstance(hdr, dict):
                hdr_text = hdr.get("ru" if self.is_ru() else "en") or hdr.get("ru") or hdr.get("en") or "MaxExteraPlugins"
            else:
                hdr_text = str(hdr)
            res.append(Header(text=hdr_text))
            res.extend(author_items)
            res.append(Divider())

        cleaned_items = []
        if original_items:
            skipping_info = False
            for item in original_items:
                item_cls = type(item).__name__
                if item_cls == "Header":
                    txt = str(getattr(item, "text", "") or getattr(item, "title", "") or "").lower()
                    if "информ" in txt or "inform" in txt:
                        skipping_info = True
                        continue
                    else:
                        skipping_info = False
                elif skipping_info and item_cls == "Divider":
                    skipping_info = False
                    continue

                if not skipping_info:
                    cleaned_items.append(item)

        res.extend(cleaned_items)
        return res

    def _dismiss_active_dialog(self):
        try:
            if self._active_dialog is not None:
                self._active_dialog.dismiss()
        except Exception:
            pass
        self._active_dialog = None

    def _is_dialog_active(self) -> bool:
        try:
            if self._active_dialog is not None:
                return bool(self._active_dialog.isShowing())
        except Exception:
            pass
        return False

    def _notify_subscribed(self):
        try:
            from ui.bulletin import BulletinHelper
            BulletinHelper.show_success(self.tr("sub_thank_you"))
        except Exception:
            pass

    def _check_initial_subscription_flow(self):
        def flow():
            try:
                if self.plugin.get_setting("never_show_sub_prompt", False):
                    return

                current_ver = str(getattr(self.plugin, "__version__", globals().get("__version__", "1.0.0")) or "1.0.0")
                last_prompted_ver = self.plugin.get_setting("last_prompted_version", None)

                # Only show on install (last_prompted_ver is None) or update (last_prompted_ver != current_ver)
                if last_prompted_ver is not None and str(last_prompted_ver) == current_ver:
                    return

                if self.is_subscribed():
                    self.plugin.set_setting("last_prompted_version", current_ver)
                    self.plugin.set_setting("was_subscribed", True)
                    return

                self._show_subscription_prompt(current_ver)
            except Exception:
                pass
        from android_utils import run_on_ui_thread
        run_on_ui_thread(flow, 1500)

    def _create_card_content(self, act, title_text, message_text):
        try:
            from android.widget import LinearLayout, TextView, ImageView
            from android.view import Gravity
            from org.telegram.messenger import AndroidUtilities
            from org.telegram.ui.ActionBar import Theme
            from client_utils import create_sticker_drawable

            dp = AndroidUtilities.dp

            layout = LinearLayout(act)
            layout.setOrientation(LinearLayout.VERTICAL)
            layout.setGravity(Gravity.CENTER_HORIZONTAL)
            layout.setPadding(dp(24), dp(20), dp(24), dp(10))

            sticker_drawable = None
            if self.icon_sticker:
                try:
                    sticker_drawable = create_sticker_drawable(self.icon_sticker, dp(120), dp(120))
                except Exception:
                    pass

            if sticker_drawable is not None:
                iv = ImageView(act)
                iv.setImageDrawable(sticker_drawable)
                lp_iv = LinearLayout.LayoutParams(dp(120), dp(120))
                lp_iv.gravity = Gravity.CENTER_HORIZONTAL
                lp_iv.bottomMargin = dp(14)
                layout.addView(iv, lp_iv)

            if title_text:
                tt = TextView(act)
                tt.setText(title_text)
                tt.setTextSize(19.0)
                tt.setTypeface(AndroidUtilities.bold())
                tt.setTextColor(Theme.getColor(Theme.key_dialogTextBlack))
                tt.setGravity(Gravity.CENTER_HORIZONTAL)
                lp_t = LinearLayout.LayoutParams(-1, -2)
                lp_t.bottomMargin = dp(8)
                layout.addView(tt, lp_t)

            if message_text:
                mt = TextView(act)
                mt.setText(message_text)
                mt.setTextSize(15.0)
                mt.setTextColor(Theme.getColor(Theme.key_dialogTextBlack))
                mt.setLineSpacing(float(dp(3)), 1.0)
                mt.setGravity(Gravity.CENTER_HORIZONTAL)
                lp_m = LinearLayout.LayoutParams(-1, -2)
                mt.setLayoutParams(lp_m)
                layout.addView(mt)

            return layout
        except Exception:
            return None

    def _show_subscription_prompt(self, current_ver: str):
        def show():
            try:
                if self._is_dialog_active(): return
                from client_utils import get_last_fragment
                frag = get_last_fragment()
                if not frag: return
                act = frag.getParentActivity()
                if not act: return

                links = self._get_links()
                url = links.get("channel_url", "https://t.me/MaxExteraPlugins")

                from ui.alert import AlertDialogBuilder
                b = AlertDialogBuilder(act)
                content = self._create_card_content(act, self.tr("install_card_title"), self.tr("install_card_msg"))
                if content is not None:
                    b.set_view(content)
                else:
                    b.set_title(self.tr("install_card_title"))
                    b.set_message(self.tr("install_card_msg"))

                def on_open_channel(dialog, which):
                    self._dismiss_active_dialog()
                    self.plugin.set_setting("last_prompted_version", current_ver)
                    self._open_url(url)

                def on_remind_later(dialog, which):
                    self._dismiss_active_dialog()
                    self.plugin.set_setting("last_prompted_version", current_ver)

                def on_never_show(dialog, which):
                    self._dismiss_active_dialog()
                    self.plugin.set_setting("never_show_sub_prompt", True)
                    self.plugin.set_setting("last_prompted_version", current_ver)

                b.set_positive_button(self.tr("open_channel_btn"), on_open_channel)
                b.set_neutral_button(self.tr("remind_later_btn"), on_remind_later)
                b.set_negative_button(self.tr("never_show_btn"), on_never_show)

                def on_dismiss(builder):
                    self.plugin.set_setting("last_prompted_version", current_ver)
                try:
                    b.set_on_dismiss_listener(on_dismiss)
                except Exception:
                    pass

                self._active_dialog = b.show()
                self.plugin.set_setting("last_prompted_version", current_ver)
            except Exception:
                pass
        from android_utils import run_on_ui_thread
        run_on_ui_thread(show)

class PluginUpdateCheckerPlugin(BasePlugin):

    def on_app_event(self, event_type):
        if hasattr(self, "_author_helper"):
            self._author_helper.on_event(event_type)
        try:
            ev_name = str(event_type).upper()
            if "RESUME" in ev_name or "START" in ev_name:
                if getattr(self, "_updates", None):
                    run_on_queue(self._reconcile_stored_updates, WORK_QUEUE, 300)
        except Exception:
            pass

    def on_plugin_load(self):
        self._author_helper = AuthorChannelHelper(self, icon_sticker=globals().get("__icon__", "MaxExteraPluginsStickers/1"))
        self._author_helper.on_load()
        self._checking = False
        self._silent_mode = False
        self._lock = threading.Lock()
        self._loading_dialog = None
        self._progress = 0
        self._progress_ts = 0
        self._total_files_to_download = 0
        self._files_downloaded = 0
        self._download_failures = 0
        self._updates = []
        self._up_to_date = []
        self._not_found = []
        self._last_scan_exists = False
        self._session = 0
        self._session_at_start = 0
        self._auto_check_pending = False
        self._wait_pending = False
        self._conn_delegate = None
        self._cache_data = {"channels": {}}
        self._new_cache_entries = {}
        self._download_priority = FileLoader.PRIORITY_HIGH
        self._incremental_since = 0
        self._channel_statuses = {}
        self._local_plugins = {}
        self._all_channel_files = []
        self._pending_downloads = deque()
        self._in_flight = {}
        self._poll_scheduled = False
        self._finalize_triggered = False
        self._download_phase_started = 0.0
        self._file_loader = None
        self._current_channel_id = 0
        self._current_channel_access_hash = 0
        self._fetch_mode = "search"
        self._deep_scan_started = False

        self._lang = "ru" if Locale.getDefault().getLanguage().startswith("ru") else "en"

        self._auto_begin_scheduled = False
        self._injected_btn = None
        self._actionbar_hooks_installed = False
        self._pulse_animator = None
        self._pulse_target = None
        self._results_dialog_holder = {"dialog": None}
        self._download_progress_base = PROGRESS_DL1_BASE
        self._download_progress_span = PROGRESS_DL1_SPAN
        self._updates = self._load_stored_updates()
        self._last_scan_exists = bool(self.get_setting("last_scan_done", False))
        self._plugins_delegate = None
        self._reconciling = False
        self._install_actionbar_hooks()
        self._register_plugins_observer()
        run_on_ui_thread(self._inject_icon_now)
        run_on_queue(self._reconcile_stored_updates, WORK_QUEUE, 500)
        if self.get_setting("auto_check", False):
            self._start_auto_check_flow()

    def _s(self, key, *args):
        text = STRINGS.get(self._lang, STRINGS["en"]).get(key, key)
        if args:
            return text.format(*args)
        return text

    def on_plugin_unload(self):
        if hasattr(self, "_author_helper"):
            self._author_helper.on_unload()
        self._stop_icon_pulse()
        self._unregister_plugins_observer()
        try:
            if self._injected_btn is not None and View is not None:
                self._injected_btn.setVisibility(View.GONE)
        except Exception:
            pass
        self._injected_btn = None
        self._auto_check_pending = False
        self._wait_pending = False
        self._session += 1
        try:
            if self._conn_delegate is not None and get_notification_center is not None and NotificationCenter is not None:
                nc = get_notification_center()
                if nc is not None:
                    nc.removeObserver(self._conn_delegate, NotificationCenter.didUpdateConnectionState, 0)
        except Exception:
            pass
        self._conn_delegate = None

    def create_settings(self):
        try:
            items = self._inner_create_settings()
        except Exception:
            items = []
        if hasattr(self, '_author_helper'):
            return self._author_helper.prepend_settings(items)
        return items

    def _inner_create_settings(self):
        return [
            Header(text=self._s("plugin_name")),
            Text(
                text=self._s("check_button"),
                icon="msg_download",
                on_click=self._on_check_click,
                link_alias="check_updates"
            ),
            Switch(
                key="auto_check",
                text=self._s("auto_check"),
                default=False,
                subtext=self._s("auto_check_sub"),
                link_alias="auto_check_updates"
            ),
            Switch(
                key="show_badge",
                text=self._s("show_badge"),
                default=True,
                subtext=self._s("show_badge_sub"),
                on_change=self._on_badge_toggle
            ),
            Header(text=self._s("ignored_header")),
            Text(
                text=self._s("ignored_manage"),
                icon="msg_clear",
                subtext=self._ignored_summary(),
                on_click=self._on_manage_ignored,
            ),
            Header(text=self._s("channels_header")),
            Text(
                text=self._s("channels_edit"),
                icon="msg_channel",
                subtext=self._get_channels_subtext(),
                on_click=self._on_channels_click,
            ),
            Header(text=self._s("history_header")),
            Text(
                text=self._s("open_results"),
                icon="msg_archive",
                subtext=self._get_last_scan_summary(),
                on_click=self._on_open_last_scan,
                link_alias="last_scan_result"
            ),
            Divider(),
        ]

    def _get_last_scan_summary(self):
        if not self._last_scan_exists:
            return self._s("no_scan")
        updates_count = len(self._updates) if self._updates else 0
        if updates_count > 0:
            return self._s("updates_available", updates_count)
        return self._s("all_up_to_date")

    def _on_open_last_scan(self, view):
        if not self._last_scan_exists:
            BulletinHelper.show_info(self._s("no_scan"))
            return
        self._show_results_dialog()

    def _get_default_custom_channels_text(self):
        return DEFAULT_CHANNELS_TEXT

    def _get_saved_custom_channels_text(self):
        return self.get_setting("custom_channels", self._get_default_custom_channels_text())

    def _get_channels_subtext(self):
        channels = self._get_channels_to_check()
        if not channels:
            return self._s("channels_hint")
        text = "@" + " @".join(channels)
        if len(text) > 120:
            text = text[:117] + "..."
        return text

    def _dp(self, value):
        try:
            if AndroidUtilities is not None:
                return AndroidUtilities.dp(value)
        except Exception:
            pass
        return int(value * 3)

    def _on_channels_click(self, view):
        self._show_channels_mode_dialog()

    def _show_channels_mode_dialog(self):
        try:
            fragment = get_last_fragment()
            if not fragment:
                return
            activity = fragment.getParentActivity()
            if not activity:
                return

            builder = AlertDialogBuilder(activity)
            builder.set_title(self._s("channels_edit"))
            current_sub = self._get_channels_subtext()
            msg = self._s("channels_choose_method")
            if current_sub:
                msg = f"{msg}\n\n{current_sub}"
            builder.set_message(msg)

            def open_picker(bld, w):
                try:
                    bld.dismiss()
                except Exception:
                    pass
                self._open_tg_channels_picker()

            def open_manual(bld, w):
                try:
                    bld.dismiss()
                except Exception:
                    pass
                self._show_channels_dialog()

            builder.set_positive_button(self._s("channels_open_tg_picker"), open_picker)
            builder.set_neutral_button(self._s("channels_enter_username"), open_manual)
            builder.set_negative_button(self._s("cancel"), lambda bld, w: bld.dismiss())
            builder.show()
        except Exception as e:
            log(f"Error showing channels mode dialog: {e}")
            self._show_channels_dialog()

    def _extract_chat_username(self, chat):
        if chat is None:
            return None
        uname = getattr(chat, "username", None)
        if uname:
            return str(uname).lstrip("@")
        try:
            usernames = getattr(chat, "usernames", None)
            if usernames is not None and usernames.size() > 0:
                for i in range(usernames.size()):
                    uobj = usernames.get(i)
                    if uobj is not None and getattr(uobj, "active", True):
                        val = getattr(uobj, "username", None)
                        if val:
                            return str(val).lstrip("@")
        except Exception:
            pass
        return None

    def _open_tg_channels_picker(self):
        try:
            fragment = get_last_fragment()
            if not fragment:
                return
            if jclass is None or dynamic_proxy is None:
                self._show_channels_dialog()
                return

            USA = jclass("org.telegram.ui.UsersSelectActivity")
            DelCls = None
            try:
                DelCls = jclass("org.telegram.ui.UsersSelectActivity$FilterUsersActivityDelegate")
            except Exception:
                DelCls = getattr(USA, "FilterUsersActivityDelegate", None)

            if USA is None or DelCls is None:
                self._show_channels_dialog()
                return

            from java.util import ArrayList
            from java.lang import Long as JLong

            current = [c.lower() for c in self._get_channels_to_check()]
            preselected = ArrayList()
            preselected_unames = set()
            mc = get_messages_controller()
            if mc is not None:
                try:
                    all_chats = mc.getAllChats()
                    if all_chats is not None:
                        for i in range(int(all_chats.size())):
                            chat = all_chats.valueAt(i)
                            uname = self._extract_chat_username(chat)
                            if uname and uname.lower() in current:
                                cid = int(getattr(chat, "id", 0) or 0)
                                if cid > 0:
                                    preselected.add(JLong(-cid))
                                    preselected_unames.add(uname.lower())
                except Exception:
                    pass

            preserved = [c for c in self._get_channels_to_check() if c.lower() not in preselected_unames]

            picker = None
            try:
                picker = USA(True, preselected, 0)
            except Exception:
                try:
                    picker = USA(False, preselected, 0)
                except Exception:
                    picker = USA(0)

            try:
                picker.noChatTypes = True
            except Exception:
                pass
            try:
                picker.doNotNewChats = True
            except Exception:
                pass

            plugin_ref = self

            class _ChannelsDelegate(dynamic_proxy(DelCls)):
                def didSelectChats(self, ids, flags):
                    try:
                        picked = []
                        had_ids = False
                        controller = get_messages_controller()
                        if ids is not None and controller is not None:
                            for i in range(int(ids.size())):
                                did = int(ids.get(i))
                                had_ids = True
                                if did < 0:
                                    chat = controller.getChat(-did)
                                    uname = plugin_ref._extract_chat_username(chat)
                                    if uname and uname not in picked:
                                        picked.append(uname)
                        if had_ids and not picked:
                            run_on_ui_thread(lambda: BulletinHelper.show_error(plugin_ref._s("channels_no_username_selected")))
                            return
                        final = list(preserved)
                        for u in picked:
                            if u.lower() not in [x.lower() for x in final]:
                                final.append(u)
                        text = " ".join(final)
                        try:
                            plugin_ref.set_setting("custom_channels", text, reload_settings=True)
                        except Exception:
                            try:
                                plugin_ref.set_setting("custom_channels", text)
                            except Exception:
                                pass
                        run_on_ui_thread(lambda: BulletinHelper.show_info(plugin_ref._s("channels_saved")))
                    except Exception as ex:
                        log(f"Error in TG channels picker delegate: {ex}\n{traceback.format_exc()}")

            picker.setDelegate(_ChannelsDelegate())
            fragment.presentFragment(picker)
        except Exception as e:
            log(f"Error opening TG channels picker: {e}\n{traceback.format_exc()}")
            self._show_channels_dialog()

    def _get_pickable_channels(self):
        try:
            controller = get_messages_controller()
            if controller is None:
                return []
            all_chats = controller.getAllChats()
            result = []
            size = int(all_chats.size())
            for i in range(size):
                chat = all_chats.valueAt(i)
                try:
                    if chat is None:
                        continue
                    if getattr(chat, "left", False):
                        continue
                    username = getattr(chat, "username", None)
                    if not username:
                        continue
                    title = getattr(chat, "title", None) or ("@" + str(username))
                    result.append({
                        "chat_id": int(getattr(chat, "id", 0)),
                        "title": str(title),
                        "username": str(username),
                    })
                except Exception:
                    continue
            result.sort(key=lambda c: c["title"].lower())
            return result
        except Exception as e:
            log(f"Error listing chats: {e}")
            return []

    def _show_channels_picker(self):
        try:
            fragment = get_last_fragment()
            if not fragment:
                return
            activity = fragment.getParentActivity()
            if not activity:
                return

            from android.widget import LinearLayout, ScrollView, TextView
            from android.graphics import Typeface

            chats = self._get_pickable_channels()
            picker_usernames = set(c["username"] for c in chats)

            root = LinearLayout(activity)
            root.setOrientation(LinearLayout.VERTICAL)
            pad = self._dp(16)
            root.setPadding(pad, pad // 2, pad, pad // 2)

            hint = TextView(activity)
            try:
                hint.setText(self._s("channels_pick_hint"))
                hint.setTextSize(14.0)
                hint.setTextColor(self._theme_color("key_dialogTextGray", 0xFF8A8A8A))
                hint.setPadding(0, self._dp(4), 0, self._dp(8))
            except Exception:
                pass
            root.addView(hint)

            count_view = TextView(activity)
            try:
                count_view.setTextSize(14.0)
                count_view.setTextColor(self._theme_color("key_dialogTextLink", 0xFF2F8CE0))
                count_view.setPadding(0, 0, 0, self._dp(6))
            except Exception:
                pass
            root.addView(count_view)

            scr = ScrollView(activity)
            lay = LinearLayout(activity)
            lay.setOrientation(LinearLayout.VERTICAL)
            scr.addView(lay)
            root.addView(scr)

            current = self._get_channels_to_check()
            preserved = [u for u in current if u not in picker_usernames]
            selected = {u: (u in current) for u in (c["username"] for c in chats)}

            state = {"selected": selected, "preserved": preserved}

            def update_count():
                try:
                    n = sum(1 for v in selected.values() if v)
                    count_view.setText(self._s("channels_pick_selected", n))
                except Exception:
                    pass

            row_views = {}
            for chat in chats:
                username = chat["username"]
                row = LinearLayout(activity)
                row.setOrientation(LinearLayout.HORIZONTAL)
                try:
                    row.setPadding(0, self._dp(8), 0, self._dp(8))
                    mark = TextView(activity)
                    left = LinearLayout(activity)
                    left.setOrientation(LinearLayout.VERTICAL)
                    title_view = TextView(activity)
                    title_view.setText(chat["title"])
                    title_view.setTextSize(15.0)
                    title_view.setTextColor(self._theme_color("key_dialogTextBlack", 0xFF1C1C1C))
                    left.addView(title_view)
                    user_view = TextView(activity)
                    user_view.setText("@" + username)
                    user_view.setTextSize(13.0)
                    user_view.setTextColor(self._theme_color("key_dialogTextGray", 0xFF8A8A8A))
                    left.addView(user_view)
                    try:
                        left_params = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0)
                    except Exception:
                        left_params = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT)
                        try:
                            left_params.weight = 1.0
                        except Exception:
                            pass
                    row.addView(left, left_params)
                    row.addView(mark)
                    row.setOnClickListener(OnClickListener(lambda v, u=username: toggle(u)))
                except Exception:
                    pass
                row_views[username] = (mark, row)
                lay.addView(row)

            def refresh_marks():
                for u, (mark, row) in row_views.items():
                    try:
                        mark.setText("\u2611" if selected.get(u) else "\u2610")
                    except Exception:
                        pass

            def toggle(username):
                try:
                    selected[username] = not selected.get(username, False)
                    refresh_marks()
                    update_count()
                except Exception:
                    pass

            refresh_marks()
            update_count()

            builder = AlertDialogBuilder(activity)
            builder.set_title(self._s("channels_pick_title"))
            builder.set_view(root)
            if chats:
                builder.set_positive_button(self._s("save"), lambda bld, w: self._save_channels_picker(state, bld))
            builder.set_neutral_button(self._s("channels_pick_manual"), lambda bld, w: self._open_manual_channels(bld))
            builder.set_negative_button(self._s("close"), lambda bld, w: bld.dismiss())

            if not chats:
                try:
                    none_view = TextView(activity)
                    none_view.setText(self._s("channels_none_available"))
                    none_view.setTextSize(14.0)
                    none_view.setTextColor(self._theme_color("key_dialogTextGray", 0xFF8A8A8A))
                    none_view.setPadding(0, self._dp(8), 0, 0)
                    lay.addView(none_view)
                except Exception:
                    pass

            dialog = builder.show()
            self._results_dialog_holder["dialog"] = dialog
        except Exception as e:
            log(f"Error showing channels picker: {e}\n{traceback.format_exc()}")
            self._show_channels_dialog()

    def _open_manual_channels(self, picker_dialog=None):
        try:
            if picker_dialog is not None:
                try:
                    picker_dialog.dismiss()
                except Exception:
                    pass
        except Exception:
            pass
        self._show_channels_dialog()

    def _save_channels_picker(self, state, dialog):
        try:
            selected = state.get("selected", {})
            preserved = state.get("preserved", [])
            final = list(preserved)
            for chat in self._get_pickable_channels():
                if selected.get(chat["username"]) and chat["username"] not in final:
                    final.append(chat["username"])
            text = " ".join(final)
            try:
                self.set_setting("custom_channels", text, reload_settings=True)
            except Exception:
                try:
                    self.set_setting("custom_channels", text)
                except Exception:
                    pass
            try:
                dialog.dismiss()
            except Exception:
                pass
            BulletinHelper.show_info(self._s("channels_saved"))
        except Exception as e:
            log(f"Error saving channels picker: {e}")

    def _show_channels_dialog(self):
        try:
            fragment = get_last_fragment()
            if not fragment:
                return
            activity = fragment.getParentActivity()
            if not activity:
                return

            from android.widget import EditText as AndroidEditText, LinearLayout, ScrollView

            current = self._get_saved_custom_channels_text()

            scr = ScrollView(activity)
            lay = LinearLayout(activity)
            lay.setOrientation(LinearLayout.VERTICAL)
            lay.setPadding(self._dp(20), self._dp(10), self._dp(20), self._dp(10))
            scr.addView(lay)

            field = AndroidEditText(activity)
            field.setHint(self._s("channels_hint"))
            field.setSingleLine(False)
            field.setMaxLines(8)
            field.setTextSize(15.0)
            if current:
                field.setText(current)
            try:
                if Theme is not None:
                    from android.graphics.drawable import GradientDrawable
                    field.setTextColor(Theme.getColor(Theme.key_chat_messagePanelText))
                    field.setHintTextColor(Theme.getColor(Theme.key_chat_messagePanelHint))
                    bg = GradientDrawable()
                    bg.setColor(Theme.getColor(Theme.key_chat_messagePanelBackground))
                    bg.setCornerRadius(self._dp(14))
                    bg.setStroke(self._dp(1), Theme.getColor(Theme.key_chat_messagePanelShadow))
                    field.setBackground(bg)
            except Exception:
                pass
            field.setPadding(self._dp(16), self._dp(12), self._dp(16), self._dp(12))
            lay.addView(field)

            builder = AlertDialogBuilder(activity)
            builder.set_title(self._s("channels_header"))
            builder.set_view(scr)
            builder.set_negative_button(self._s("cancel"), lambda bld, w: bld.dismiss())
            builder.set_positive_button(self._s("save"), lambda bld, w: self._save_channels_from_dialog(field, bld))
            builder.show()
        except Exception as e:
            log(f"Error showing channels dialog: {e}\n{traceback.format_exc()}")

    def _save_channels_from_dialog(self, field, dialog):
        text = ""
        try:
            text = str(field.getText().toString())
        except Exception:
            try:
                text = str(field.getText())
            except Exception:
                text = ""
        try:
            self.set_setting("custom_channels", text, reload_settings=True)
        except Exception:
            try:
                self.set_setting("custom_channels", text)
            except Exception:
                pass
        try:
            dialog.dismiss()
        except Exception:
            pass
        BulletinHelper.show_info(self._s("channels_saved"))

    def _load_stored_updates(self):
        try:
            raw = self.get_setting("last_updates_json", "")
            if raw:
                data = json.loads(raw)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
        return []

    def _store_last_results(self):
        try:
            self.set_setting("last_updates_json", json.dumps(self._updates))
            self.set_setting("last_scan_done", True)
        except Exception:
            pass

    def _install_actionbar_hooks(self):
        if self._actionbar_hooks_installed or find_class is None:
            return
        hook_all = getattr(self, "hook_all_methods", None)
        if hook_all is None:
            return
        try:
            dialogs_clazz = find_class("org.telegram.ui.DialogsActivity")
            if dialogs_clazz is None:
                return
            hook_all(dialogs_clazz, "createView", _DialogsCreateViewHook(self))
            hook_all(dialogs_clazz, "onResume", _DialogsResumeHook(self))
            hook_all(dialogs_clazz, "onBecomeFullyVisible", _DialogsVisibleHook(self))
            self._actionbar_hooks_installed = True
        except Exception:
            self._actionbar_hooks_installed = False

    def _is_main_dialogs_screen(self, fragment):
        try:
            if fragment is None:
                return False
            if fragment.getClass().getName() != "org.telegram.ui.DialogsActivity":
                return False
            try:
                if int(fragment.folderId) != 0:
                    return False
            except Exception:
                pass
            try:
                if bool(fragment.onlySelect):
                    return False
            except Exception:
                pass
            return True
        except Exception:
            return False

    def _inject_icon_now(self):
        try:
            fragment = get_last_fragment()
            if fragment is None:
                return
            if not self._is_main_dialogs_screen(fragment):
                return
            self._add_icon_to_fragment(fragment)
        except Exception:
            pass

    def _update_actionbar_icon(self):
        try:
            btn = self._injected_btn
            if btn is None or View is None:
                return
            show = bool(self.get_setting("show_badge", True)) and bool(self._updates)
            btn.setVisibility(View.VISIBLE if show else View.GONE)
            if show:
                self._start_icon_pulse(btn)
            else:
                self._stop_icon_pulse()
        except Exception:
            pass

    def _get_pulse_insets(self, item):
        try:
            w = int(item.getWidth()) if item is not None else 0
            h = int(item.getHeight()) if item is not None else 0
        except Exception:
            w = 0
            h = 0
        if w <= 0 or h <= 0:
            w = self._dp(48)
            h = self._dp(56)
        pad = self._dp(2)
        diff = h - w
        if diff > 0:
            top = (diff // 2) + pad
            bottom = (diff - diff // 2) + pad
            left = pad
            right = pad
            return left, top, right, bottom
        elif diff < 0:
            left = ((-diff) // 2) + pad
            right = ((-diff) - (-diff) // 2) + pad
            top = pad
            bottom = pad
            return left, top, right, bottom
        return pad, pad, pad, pad

    def _start_icon_pulse(self, item):
        if _PulseUpdateListener is None or ValueAnimator is None:
            return
        if self._pulse_animator is not None and self._pulse_target is item:
            return
        self._stop_icon_pulse()
        drawable = None
        if GradientDrawable is not None:
            try:
                drawable = GradientDrawable()
                drawable.setShape(GradientDrawable.OVAL)
                drawable.setColor(0)
                try:
                    drawable.mutate()
                except Exception:
                    pass
                applied_drawable = drawable
                if InsetDrawable is not None:
                    try:
                        left, top, right, bottom = self._get_pulse_insets(item)
                        applied_drawable = InsetDrawable(drawable, left, top, right, bottom)
                    except Exception:
                        applied_drawable = drawable
                item.setBackground(applied_drawable)
            except Exception:
                drawable = None
        try:
            anim = ValueAnimator.ofFloat(0.0, 1.0)
            anim.setDuration(PULSE_DURATION_MS)
            anim.setRepeatCount(ValueAnimator.INFINITE)
            anim.setRepeatMode(ValueAnimator.REVERSE)
            anim.addUpdateListener(_PulseUpdateListener(self, item, drawable))
            anim.start()
            self._pulse_animator = anim
            self._pulse_target = item
            if InsetDrawable is not None and drawable is not None and item is not None:
                def update_insets():
                    try:
                        if self._pulse_target is item:
                            left, top, right, bottom = self._get_pulse_insets(item)
                            item.setBackground(InsetDrawable(drawable, left, top, right, bottom))
                    except Exception:
                        pass
                try:
                    item.post(update_insets)
                except Exception:
                    pass
        except Exception:
            self._pulse_animator = None
            self._pulse_target = None
            try:
                item.setBackground(None)
            except Exception:
                pass

    def _stop_icon_pulse(self):
        anim = self._pulse_animator
        self._pulse_animator = None
        self._pulse_target = None
        if anim is not None:
            try:
                anim.cancel()
            except Exception:
                pass
        btn = self._injected_btn
        if btn is not None:
            try:
                btn.setBackground(None)
            except Exception:
                pass

    def _on_updates_reconciled(self):
        try:
            self._update_actionbar_icon()
            self._inject_icon_now()
        except Exception:
            pass

    def _reconcile_stored_updates(self):
        try:
            if not self._updates:
                return
            if getattr(self, "_reconciling", False):
                return
            self._reconciling = True
            try:
                local = self._get_local_plugins()
                kept = []
                changed = False
                for u in self._updates:
                    pid = u.get("plugin_id")
                    channel_ver = str(u.get("channel_version", ""))
                    li = local.get(pid)
                    if li is None:
                        # Plugin was deleted or uninstalled - remove from available updates
                        changed = True
                        if hasattr(self, "_up_to_date") and isinstance(self._up_to_date, list):
                            self._up_to_date = [item for item in self._up_to_date if item.get("plugin_id") != pid]
                        if hasattr(self, "_not_found") and isinstance(self._not_found, list):
                            self._not_found = [item for item in self._not_found if item.get("plugin_id") != pid]
                        continue

                    local_ver = str(li.get("version", ""))
                    if not self._version_is_newer(channel_ver, local_ver):
                        # Plugin was updated to current or newer version
                        changed = True
                        if hasattr(self, "_up_to_date") and isinstance(self._up_to_date, list):
                            self._up_to_date = [item for item in self._up_to_date if item.get("plugin_id") != pid]
                            self._up_to_date.append({
                                "plugin_id": pid,
                                "name": li.get("name") or u.get("name", pid),
                                "version": local_ver,
                                "channel_id": u.get("channel_id"),
                                "channel_username": u.get("channel_username"),
                                "message_id": u.get("message_id"),
                            })
                        continue
                    kept.append(u)
                if changed:
                    self._updates = kept
                    self._store_last_results()
                    run_on_ui_thread(self._on_updates_reconciled)
            finally:
                self._reconciling = False
        except Exception as e:
            self._reconciling = False
            log(f"Error in _reconcile_stored_updates: {e}")

    def _add_icon_to_fragment(self, fragment):
        try:
            if not self.get_setting("show_badge", True):
                if self._injected_btn is not None and View is not None:
                    try:
                        self._injected_btn.setVisibility(View.GONE)
                    except Exception:
                        pass
                return True
            if not self._is_main_dialogs_screen(fragment):
                return False
            if View is None or jclass is None or OnClickListener is None:
                return False
            actionBar = fragment.getActionBar()
            if not actionBar:
                return False
            menu = actionBar.createMenu()
            if menu is None:
                return False
            try:
                existing = menu.getItem(PUC_BUTTON_ID)
            except Exception:
                existing = None
            if existing is not None:
                self._injected_btn = existing
                self._update_actionbar_icon()
                return True
            R_drawable = jclass("org.telegram.messenger.R$drawable")
            icon_res = getattr(R_drawable, "msg_download", getattr(R_drawable, "msg_retry", 0))
            item = menu.addItem(PUC_BUTTON_ID, icon_res)
            menu.removeView(item)
            idx = max(0, menu.getChildCount() - 1)
            menu.addView(item, idx)
            item.setOnClickListener(OnClickListener(lambda v: self._show_results_dialog()))
            self._injected_btn = item
            self._update_actionbar_icon()
            return True
        except Exception:
            return False

    def _on_badge_toggle(self, enabled):
        run_on_ui_thread(self._inject_icon_now)

    def _on_check_click(self, view):
        if self._checking:
            if not self._silent_mode and self._progress > 0 and time.time() - getattr(self, "_check_started_ts", 0) < 60.0:
                self._show_loading_dialog()
                return
            self._end_check()
        self._silent_mode = False
        self._progress = 0
        self._progress_ts = 0
        self._last_progress_message = self._s("reading_plugins")
        self._show_loading_dialog()
        self._run_bg(self._start_check, 0)

    def _start_queued_check(self):
        run_on_queue(self._start_check, WORK_QUEUE, 0)

    def _start_auto_check_flow(self):
        try:
            if time.time() - float(self.get_setting("last_check_ts", 0) or 0) < AUTO_CHECK_MIN_INTERVAL_S:
                return
        except Exception:
            pass
        self._silent_mode = True
        self._auto_check_pending = True
        self._register_conn_observer()
        if self._is_online():
            self._schedule_delayed_auto_begin()
        elif _ConnectionStateDelegate is None:
            self._wait_for_connection(self._schedule_delayed_auto_begin, lambda: None)

    def _schedule_delayed_auto_begin(self):
        if not self._auto_check_pending or self._auto_begin_scheduled:
            return
        self._auto_begin_scheduled = True
        scheduled_session = self._session

        def begin():
            self._auto_begin_scheduled = False
            if not self._auto_check_pending or self._checking:
                return
            if self._session != scheduled_session:
                return
            if not self._is_online():
                return
            try:
                if time.time() - float(self.get_setting("last_check_ts", 0) or 0) < AUTO_CHECK_MIN_INTERVAL_S:
                    self._auto_check_pending = False
                    return
            except Exception:
                pass
            self._auto_check_pending = False
            self._silent_mode = True
            run_on_queue(self._start_check, WORK_QUEUE, 0)

        run_on_queue(begin, WORK_QUEUE, AUTO_CHECK_DELAY_MS)

    def _register_plugins_observer(self):
        try:
            if getattr(self, "_plugins_delegate", None) is not None:
                return
            if NotificationCenter is None or _PluginsUpdatedDelegate is None:
                return
            plugins_updated_id = getattr(NotificationCenter, "pluginsUpdated", None)
            if plugins_updated_id is None:
                return
            delegate = _PluginsUpdatedDelegate(self)
            self._plugins_delegate = delegate
            try:
                NotificationCenter.getGlobalInstance().addObserver(delegate, int(plugins_updated_id))
            except Exception:
                pass
            try:
                if get_notification_center is not None:
                    nc = get_notification_center()
                    if nc is not None and nc != NotificationCenter.getGlobalInstance():
                        nc.addObserver(delegate, int(plugins_updated_id))
            except Exception:
                pass
        except Exception as e:
            log(f"Error registering plugins observer: {e}")

    def _unregister_plugins_observer(self):
        delegate = getattr(self, "_plugins_delegate", None)
        if delegate is None or NotificationCenter is None:
            return
        plugins_updated_id = getattr(NotificationCenter, "pluginsUpdated", None)
        if plugins_updated_id is not None:
            try:
                NotificationCenter.getGlobalInstance().removeObserver(delegate, int(plugins_updated_id))
            except Exception:
                pass
            try:
                if get_notification_center is not None:
                    nc = get_notification_center()
                    if nc is not None:
                        nc.removeObserver(delegate, int(plugins_updated_id))
            except Exception:
                pass
        self._plugins_delegate = None

    def _on_plugins_updated_notification(self):
        if getattr(self, "_updates", None):
            run_on_queue(self._reconcile_stored_updates, WORK_QUEUE, 100)

    def _register_conn_observer(self):
        try:
            if _ConnectionStateDelegate is None or get_notification_center is None or NotificationCenter is None:
                return
            nc = get_notification_center()
            if nc is None:
                return
            self._conn_delegate = _ConnectionStateDelegate(self)
            nc.addObserver(self._conn_delegate, NotificationCenter.didUpdateConnectionState, 0)
        except Exception:
            self._conn_delegate = None

    def _wait_for_connection(self, callback, on_timeout=None):
        attempts = max(int(CONNECTION_WAIT_TIMEOUT_S * 1000.0 / CONNECTION_POLL_MS), 1)

        def tick(remaining):
            if not self._wait_pending:
                return
            if self._is_online():
                self._wait_pending = False
                callback()
                return
            if remaining <= 0:
                self._wait_pending = False
                if on_timeout is not None:
                    on_timeout()
                else:
                    callback()
                return
            run_on_queue(lambda: tick(remaining - 1), WORK_QUEUE, CONNECTION_POLL_MS)

        self._wait_pending = True
        if self._is_online():
            self._wait_pending = False
            callback()
            return
        run_on_queue(lambda: tick(attempts), WORK_QUEUE, 0)

    def _on_connection_state(self):
        if not self._auto_check_pending:
            return
        if self._is_online():
            self._schedule_delayed_auto_begin()

    def _is_online(self):
        try:
            if get_connections_manager is None:
                return True
            manager = get_connections_manager()
            if manager is None:
                return True
            get_state = getattr(manager, "getCurrentState", None)
            if get_state is None:
                return True
            return int(get_state()) in ONLINE_CONNECTION_STATES
        except Exception:
            return True

    def _run_bg(self, fn, delay_ms=0):
        res = None
        try:
            res = run_on_queue(fn, WORK_QUEUE, delay_ms)
        except Exception as e:
            log(f"run_on_queue error ({WORK_QUEUE}): {e}")
        if res is None and WORK_QUEUE != PLUGINS_QUEUE:
            try:
                res = run_on_queue(fn, PLUGINS_QUEUE, delay_ms)
            except Exception as e:
                log(f"run_on_queue fallback error (PLUGINS_QUEUE): {e}")
        if res is None:
            def runner():
                if delay_ms > 0:
                    time.sleep(delay_ms / 1000.0)
                try:
                    fn()
                except Exception as ex:
                    log(f"bg thread error: {ex}\n{traceback.format_exc()}")
            threading.Thread(target=runner, daemon=True).start()

    def _start_check(self):
        with self._lock:
            if self._checking:
                return
            self._checking = True
            self._check_started_ts = time.time()
        try:
            self._start_check_inner()
        except Exception as e:
            log(f"Fatal error in _start_check: {e}\n{traceback.format_exc()}")
            self._end_check()
            if not self._silent_mode:
                run_on_ui_thread(self._dismiss_loading_dialog)
                run_on_ui_thread(lambda: BulletinHelper.show_error(f"Error: {e}"))

    def _start_check_inner(self):
        self._session += 1
        self._session_at_start = self._session
        p_norm = getattr(FileLoader, "PRIORITY_NORMAL", 0)
        p_high = getattr(FileLoader, "PRIORITY_HIGH", 1)
        self._download_priority = p_norm if self._silent_mode else p_high
        self._incremental_since = 0
        if self._silent_mode:
            try:
                last_ts = float(self.get_setting("last_check_ts", 0) or 0)
                last_full = float(self.get_setting("last_full_scan_ts", 0) or 0)
            except Exception:
                last_ts = 0.0
                last_full = 0.0
            # the incremental window only sees posts newer than the previous
            # check, so a periodically repeated full scan recovers anything
            # that was ever missed (channel error, cancelled check, clock skew)
            if last_ts > 0 and time.time() - last_full < FULL_SCAN_MIN_INTERVAL_S:
                self._incremental_since = max(0, int(last_ts - INCREMENTAL_SLACK_S))
        self._fetch_mode = "search"
        self._deep_scan_started = False
        self._new_cache_entries = {}
        self._updates = []
        self._up_to_date = []
        self._not_found = []
        self._channel_plugins = {}
        self._channel_statuses = {}
        self._all_channel_files = []
        self._pending_downloads = deque()
        self._in_flight = {}
        self._poll_scheduled = False
        self._finalize_triggered = False
        self._files_downloaded = 0
        self._total_files_to_download = 0
        self._download_failures = 0

        self._set_progress(2, self._s("reading_plugins"))
        try:
            local_plugins = self._get_local_plugins()
            self._cache_data = self._load_cache()
        except Exception as e:
            log(f"Error reading plugins: {e}\n{traceback.format_exc()}")
            local_plugins = {}
            self._cache_data = {"channels": {}}

        if not local_plugins:
            self._end_check()
            if not self._silent_mode:
                run_on_ui_thread(self._dismiss_loading_dialog)
                run_on_ui_thread(lambda: self._show_simple_result(self._s("no_plugins")))
            return

        self._local_plugins = local_plugins
        channels = self._get_channels_to_check()
        if not channels:
            self._end_check()
            if not self._silent_mode:
                run_on_ui_thread(self._dismiss_loading_dialog)
                run_on_ui_thread(lambda: self._show_simple_result(self._s("no_channels")))
            return

        self._channels_to_check = channels
        self._total_channels = len(channels)
        self._current_channel_index = 0
        self._set_progress(5, self._s("found_plugins", len(local_plugins), self._total_channels))
        self._resolve_next_channel()

    def _end_check(self):
        with self._lock:
            self._checking = False
        self._wait_pending = False
        self._session += 1

    def _session_changed(self):
        return self._session != self._session_at_start

    def _send_tg_request(self, req, fn):
        try:
            send_request(req, fn)
        except TypeError:
            try:
                send_request(req, RequestCallback(fn))
            except Exception as e:
                log(f"send_request fallback failed: {e}\n{traceback.format_exc()}")
                raise

    def _schedule_channel_watchdog(self, channel, step_name, timeout_s=30.0):
        expected_session = self._session
        expected_index = self._current_channel_index
        def watchdog():
            if self._session != expected_session or self._current_channel_index != expected_index:
                return
            log(f"Channel request timeout for @{channel} during {step_name}")
            self._current_channel_error = "timeout"
            self._finish_current_channel()
        run_on_queue(watchdog, WORK_QUEUE, int(timeout_s * 1000.0))

    def _resolve_next_channel(self):
        if self._session_changed():
            return
        if self._current_channel_index >= len(self._channels_to_check):
            self._start_downloading_all_files()
            return

        channel = self._channels_to_check[self._current_channel_index]
        self._current_channel_username = channel
        self._current_channel_fetched_messages = []
        self._current_channel_error = None
        self._current_channel_pages = 0

        if self._fetch_mode == "history":
            chan_pct = PROGRESS_DEEP_BASE + int(PROGRESS_DEEP_SPAN * self._current_channel_index / max(self._total_channels, 1))
            self._set_progress(chan_pct, self._s("deep_scan_channel", channel, self._current_channel_index + 1, self._total_channels))
        else:
            chan_pct = PROGRESS_SEARCH_BASE + int(PROGRESS_SEARCH_SPAN * self._current_channel_index / max(self._total_channels, 1))
            self._set_progress(chan_pct, self._s("resolving_channel", channel, self._current_channel_index + 1, self._total_channels))

        self._schedule_channel_watchdog(channel, "resolve")
        try:
            req = TLRPC.TL_contacts_resolveUsername()
            req.username = channel
            self._send_tg_request(req, self._on_channel_resolved)
        except Exception as e:
            log(f"Error resolving channel {channel}: {e}\n{traceback.format_exc()}")
            self._current_channel_error = "resolve error"
            self._finish_current_channel()

    def _on_channel_resolved(self, response, error):
        if self._session_changed():
            return
        try:
            if error is not None or response is None:
                self._current_channel_error = self._error_text(error, "resolve failed")
                self._finish_current_channel()
                return

            chats = getattr(response, "chats", None)
            users = getattr(response, "users", None)

            if chats is not None and chats.size() > 0:
                get_messages_controller().putChats(chats, False)
            if users is not None and users.size() > 0:
                get_messages_controller().putUsers(users, False)

            if chats is None or chats.size() == 0:
                if users is not None and users.size() > 0:
                    self._current_channel_error = "not a channel (bot or user)"
                else:
                    self._current_channel_error = "no access, join the channel if it is private"
                self._finish_current_channel()
                return

            channel = chats.get(0)
            self._current_channel_id = channel.id
            self._current_channel_access_hash = channel.access_hash

            frac = (self._current_channel_index + 0.4) / max(self._total_channels, 1)
            if self._fetch_mode == "history":
                chan_pct = PROGRESS_DEEP_BASE + int(PROGRESS_DEEP_SPAN * frac)
            else:
                chan_pct = PROGRESS_SEARCH_BASE + int(PROGRESS_SEARCH_SPAN * frac)
            self._set_progress(chan_pct, self._s("searching_channel", self._current_channel_username))
            self._fetch_channel_documents(0)

        except Exception as e:
            log(f"Error in channel resolution: {e}\n{traceback.format_exc()}")
            self._current_channel_error = "resolve error"
            self._finish_current_channel()

    def _fetch_channel_documents(self, offset_id):
        if self._session_changed():
            return
        self._current_channel_pages += 1
        if self._fetch_mode == "history":
            if self._current_channel_pages > MAX_DEEP_SCAN_PAGES:
                self._current_channel_error = "too many history pages"
                self._finish_current_channel()
                return
        elif self._current_channel_pages > MAX_HISTORY_PAGES:
            self._current_channel_error = "too many search pages"
            self._finish_current_channel()
            return

        frac = (self._current_channel_index + 0.4) / max(self._total_channels, 1)
        try:
            peer = TLRPC.TL_inputPeerChannel()
            peer.channel_id = self._current_channel_id
            peer.access_hash = self._current_channel_access_hash

            if self._fetch_mode == "history":
                self._set_progress(PROGRESS_DEEP_BASE + int(PROGRESS_DEEP_SPAN * frac), self._s("deep_scan_page", self._current_channel_username, self._current_channel_pages))
                req = TLRPC.TL_messages_getHistory()
                req.peer = peer
                req.offset_id = offset_id
                req.offset_date = 0
                req.add_offset = 0
                req.limit = HISTORY_PAGE_LIMIT
                req.max_id = 0
                req.min_id = 0
                req.hash = 0
            else:
                self._set_progress(PROGRESS_SEARCH_BASE + int(PROGRESS_SEARCH_SPAN * frac), self._s("searching_page", self._current_channel_username, self._current_channel_pages))
                req = TLRPC.TL_messages_search()
                req.limit = HISTORY_PAGE_LIMIT
                # empty query + document filter returns every document in
                # the channel regardless of caption text (server-side search
                # matches captions, not file names); .plugin files are
                # filtered locally by file name
                req.q = ""
                req.filter = TLRPC.TL_inputMessagesFilterDocument()
                req.min_date = self._incremental_since
                req.max_date = 0
                req.offset_id = offset_id
                req.add_offset = 0
                req.max_id = 0
                req.min_id = 0
                req.hash = 0
                req.from_id = None
                req.saved_peer_id = None
                req.saved_reaction = None
                req.top_msg_id = 0
                req.flags = 0
                req.peer = peer

            self._schedule_channel_watchdog(self._current_channel_username, f"fetch page {self._current_channel_pages}")
            self._send_tg_request(req, self._on_documents_fetched)
        except Exception as e:
            log(f"Error searching documents: {e}\n{traceback.format_exc()}")
            self._current_channel_error = "search failed"
            self._finish_current_channel()

    def _on_documents_fetched(self, response, error):
        if self._session_changed():
            return
        try:
            if error is not None or response is None:
                self._current_channel_error = self._error_text(error, "search failed")
                self._finish_current_channel()
                return

            messages = response.messages
            if messages is None:
                self._finish_current_channel()
                return

            size = messages.size()
            if size > 0:
                for i in range(size):
                    self._current_channel_fetched_messages.append(messages.get(i))

            if size >= HISTORY_PAGE_LIMIT:
                last_id = messages.get(size - 1).id
                self._fetch_channel_documents(last_id)
            else:
                self._finish_current_channel()

        except Exception as e:
            log(f"Error processing search results: {e}")
            self._current_channel_error = "search parse error"
            self._finish_current_channel()

    def _finish_current_channel(self):
        if self._session_changed():
            return
        try:
            username = self._current_channel_username or ""
            files = self._collect_current_channel_files()
            self._channel_statuses[username] = {
                "error": self._current_channel_error,
                "files": len(files),
            }
        except Exception as e:
            log(f"Error finishing channel: {e}")
        self._current_channel_index += 1
        self._resolve_next_channel()

    def _collect_current_channel_files(self):
        seen = {}
        try:
            for msg in self._current_channel_fetched_messages:
                media = getattr(msg, "media", None)
                if media is None:
                    continue
                doc = getattr(media, "document", None)
                if doc is None:
                    continue

                filename = self._get_document_filename(doc)
                if not filename or not filename.lower().endswith((".plugin", ".elyx", ".eaf")):
                    continue

                doc_id = int(doc.id)
                key = (filename, doc_id)
                existing = seen.get(key)
                if existing is None or msg.id > existing["message_id"]:
                    seen[key] = {
                        "filename": filename,
                        "doc_id": int(doc.id),
                        "date": int(getattr(msg, "date", 0) or 0),
                        "message_id": int(msg.id),
                        "channel_id": self._current_channel_id,
                        "channel_username": self._current_channel_username or "",
                        "document": doc,
                        "message": msg,
                    }
        except Exception as e:
            log(f"Error collecting channel files: {e}")

        username = self._current_channel_username or ""
        old_channel_cache = self._cache_data.get("channels", {}).get(username, {})

        for _key, e in seen.items():
            cached = None
            docs_cache = old_channel_cache.get(e["filename"])
            if isinstance(docs_cache, dict):
                docs = docs_cache.get("docs")
                if isinstance(docs, dict):
                    cached = docs.get(str(e["doc_id"]))
            if cached is not None and cached.get("plugin_id") and cached.get("version"):
                e["cached"] = True
                e["plugin_id"] = cached["plugin_id"]
                e["version"] = cached["version"]
                e["name"] = cached.get("name") or ""
            else:
                e["cached"] = False
            self._all_channel_files.append(e)

        return seen

    def _start_downloading_all_files(self):
        if self._session_changed():
            return
        try:
            self._file_loader = get_file_loader()
        except Exception:
            self._file_loader = None

        self._pending_downloads = deque()
        self._in_flight = {}
        self._poll_scheduled = False
        self._finalize_triggered = False
        self._download_phase_started = time.time()
        if self._fetch_mode == "history":
            self._download_progress_base = PROGRESS_DL2_BASE
            self._download_progress_span = PROGRESS_DL2_SPAN
        else:
            self._download_progress_base = PROGRESS_DL1_BASE
            self._download_progress_span = PROGRESS_DL1_SPAN

        # the same file name can carry different plugin versions in other
        # channels and even in other messages of the same channel, so every
        # unique document (channel, filename, doc_id) is queued, the newest
        # message being kept per document; the best version overall is then
        # chosen by _record_channel_result, and identical documents shared
        # across channels (forwards, same doc_id) are downloaded only once
        best_entries = {}
        for entry in self._all_channel_files:
            try:
                if entry.get("cached"):
                    self._record_channel_result(entry, entry.get("version"), entry.get("name") or entry["filename"], entry.get("plugin_id"))
                    continue
                key = (entry["channel_username"], entry["filename"], entry["doc_id"])
                current = best_entries.get(key)
                if current is None or entry["message_id"] > current["message_id"]:
                    best_entries[key] = entry
            except Exception:
                continue

        seen_doc_ids = set()
        for entry in best_entries.values():
            doc_id = entry.get("doc_id")
            if doc_id is not None and doc_id in seen_doc_ids:
                continue
            if doc_id is not None:
                seen_doc_ids.add(doc_id)
            self._pending_downloads.append(entry)

        self._total_files_to_download = len(self._pending_downloads)
        self._files_downloaded = 0
        self._download_failures = 0

        if not self._pending_downloads:
            self._finish_downloads_phase()
            return

        self._set_progress(self._download_progress_base, self._s("downloading_files", self._total_files_to_download))
        self._schedule_poll()

    def _schedule_poll(self):
        if self._poll_scheduled or self._finalize_triggered:
            return
        self._poll_scheduled = True
        run_on_queue(self._poll_downloads, WORK_QUEUE, POLL_INTERVAL_MS)

    def _poll_downloads(self):
        self._poll_scheduled = False
        if self._session_changed() or self._finalize_triggered:
            return

        file_loader = self._file_loader
        if file_loader is None:
            try:
                file_loader = get_file_loader()
                self._file_loader = file_loader
            except Exception:
                file_loader = None
        if file_loader is None:
            self._finish_downloads_phase()
            return

        processed = 0
        while self._pending_downloads and processed < FILES_PER_POLL:
            processed += 1
            entry = self._pending_downloads[0]
            doc = entry["document"]
            try:
                file_path = file_loader.getPathToAttach(doc)
                if file_path is not None and file_path.exists():
                    expected = max(int(getattr(doc, "size", 0) or 0), 1)
                    if file_path.length() >= expected:
                        self._pending_downloads.popleft()
                        self._in_flight.pop(id(entry), None)
                        self._handle_file_done(file_path, entry)
                        continue
            except Exception:
                pass

            entry["attempts"] = entry.get("attempts", 0) + 1
            if entry["attempts"] >= MAX_DOWNLOAD_ATTEMPTS:
                self._pending_downloads.popleft()
                self._in_flight.pop(id(entry), None)
                self._files_downloaded += 1
                self._download_failures += 1
                continue

            if id(entry) not in self._in_flight:
                if len(self._in_flight) < MAX_CONCURRENT_DOWNLOADS:
                    try:
                        file_loader.loadFile(doc, entry["message"], self._download_priority, 0)
                        self._in_flight[id(entry)] = True
                    except Exception as e:
                        log(f"loadFile error: {e}")
            elif entry["attempts"] % RELOAD_EVERY_ATTEMPTS == 0:
                try:
                    file_loader.loadFile(doc, entry["message"], self._download_priority, 0)
                except Exception:
                    pass

        finished = self._total_files_to_download - len(self._pending_downloads)
        self._set_progress(
            self._download_progress_base + int(self._download_progress_span * finished / max(self._total_files_to_download, 1)),
            self._s("downloading_progress", finished, self._total_files_to_download),
        )

        if not self._pending_downloads:
            self._finish_downloads_phase()
            return
        self._schedule_poll()

    def _handle_file_done(self, file_path, entry):
        try:
            fname = (entry.get("filename") or "").lower()
            if fname.endswith((".elyx", ".eaf")):
                meta = self._parse_elyx_file(str(file_path))
            else:
                content = self._read_plugin_file(str(file_path))
                meta = self._parse_plugin_metadata(content) if content else None
            if meta and meta.get("id") and meta.get("version"):
                self._record_channel_result(entry, meta["version"], meta.get("name") or meta["id"], meta["id"])
                return
        except Exception as e:
            log(f"Error parsing downloaded file {entry.get('filename')}: {e}")
        self._download_failures += 1

    def _parse_elyx_file(self, file_path):
        try:
            import zipfile
            with zipfile.ZipFile(file_path, "r") as zf:
                names = set(zf.namelist())
                meta_name = None
                for cand in ("metainfo.yml", "metainfo.yaml", "metainfo.json"):
                    if cand in names:
                        meta_name = cand
                        break
                if meta_name is None:
                    for cand in ("refmap.yml", "refmap.yaml"):
                        if cand in names:
                            try:
                                ref = self._parse_elyx_meta_text(zf.read(cand).decode("utf-8", errors="replace"))
                                pointed = (ref.get("metainfo") or "").strip()
                                if pointed and pointed in names:
                                    meta_name = pointed
                            except Exception:
                                pass
                            break
                if meta_name is None:
                    return None
                meta = self._parse_elyx_meta_raw(
                    zf.read(meta_name).decode("utf-8", errors="replace"), meta_name)
                if meta and meta.get("id") and not meta.get("version"):
                    meta["version"] = "1.0.0"
                return meta
        except Exception as e:
            log(f"Error parsing elyx file {entry_name(file_path)}: {e}")
            return None

    def _parse_elyx_meta_raw(self, raw, name):
        if name.endswith(".json"):
            try:
                data = json.loads(raw)
                return {
                    "id": str(data.get("id", "")).strip(),
                    "name": str(data.get("name", "")).strip(),
                    "version": str(data.get("version", "")).strip(),
                }
            except Exception:
                return None
        return self._parse_elyx_meta_text(raw)

    def _parse_elyx_meta_text(self, raw):
        meta = {}
        for line in raw.splitlines():
            m = re.match(r'^[ \t]*([A-Za-z_][A-Za-z0-9_]*)[ \t]*:[ \t]*(.*)$', line)
            if not m:
                continue
            key = m.group(1).lower()
            if key not in ("id", "name", "version", "metainfo"):
                continue
            val = m.group(2).strip()
            q = re.match(r'^(["\'])(.*)\1[ \t]*$', val)
            if q:
                val = q.group(2)
            else:
                val = re.split(r'[ \t]#', val)[0].strip()
            if val and key not in meta:
                meta[key] = val
        return meta

    def _record_channel_result(self, entry, version, name, plugin_id):
        try:
            existing = self._channel_plugins.get(plugin_id)
            if existing is None or self._version_is_newer(str(version), str(existing.get("version", ""))):
                self._channel_plugins[plugin_id] = {
                    "version": str(version),
                    "name": name,
                    "channel_id": entry["channel_id"],
                    "channel_username": entry["channel_username"],
                    "message_id": entry["message_id"],
                    "filename": entry["filename"],
                }
            try:
                channel_cache = self._new_cache_entries.setdefault(entry["channel_username"], {})
                entry_cache = channel_cache.setdefault(entry["filename"], {"docs": {}})
                docs = entry_cache.get("docs")
                if not isinstance(docs, dict):
                    docs = {}
                    entry_cache["docs"] = docs
                docs[str(entry["doc_id"])] = {
                    "plugin_id": plugin_id,
                    "version": str(version),
                    "name": name,
                }
            except Exception:
                pass
        except Exception as e:
            log(f"Error recording channel result: {e}")

    def _finish_downloads_phase(self):
        if self._finalize_triggered:
            return
        self._finalize_triggered = True
        self._finalize_all_channels()

    def _begin_deep_scan(self):
        if self._session_changed():
            return
        self._deep_scan_started = True
        self._fetch_mode = "history"
        self._current_channel_index = 0
        self._current_channel_fetched_messages = []
        self._current_channel_error = None
        self._current_channel_pages = 0
        self._pending_downloads = deque()
        self._in_flight = {}
        self._poll_scheduled = False
        self._finalize_triggered = False
        self._files_downloaded = 0
        self._total_files_to_download = 0
        self._download_failures = 0

        self._set_progress(PROGRESS_DEEP_INTRO, self._s("deep_scan_phase"))
        self._resolve_next_channel()

    def _finalize_all_channels(self):
        try:
            self._save_cache()
            updates = []
            up_to_date = []
            not_found = []

            ignored = self._get_ignored_map()
            for pid, local_info in self._local_plugins.items():
                if pid in self._channel_plugins:
                    channel_info = self._channel_plugins[pid]
                    local_ver = local_info["version"]
                    channel_ver = channel_info["version"]
                    if self._version_is_newer(channel_ver, local_ver):
                        if self._is_update_ignored(pid, channel_ver, ignored):
                            continue
                        updates.append({
                            "plugin_id": pid,
                            "name": local_info["name"],
                            "local_version": local_ver,
                            "channel_version": channel_ver,
                            "channel_id": channel_info["channel_id"],
                            "channel_username": channel_info["channel_username"],
                            "message_id": channel_info["message_id"],
                        })
                    else:
                        up_to_date.append({
                            "plugin_id": pid,
                            "name": local_info["name"],
                            "version": local_ver,
                            "channel_id": channel_info["channel_id"],
                            "channel_username": channel_info["channel_username"],
                            "message_id": channel_info["message_id"],
                        })
                else:
                    not_found.append({
                        "plugin_id": pid,
                        "name": local_info["name"],
                    })

            self._updates = updates
            self._up_to_date = up_to_date
            self._not_found = not_found

            if not_found and not self._deep_scan_started:
                deep_scan_allowed = not self._silent_mode
                if not deep_scan_allowed:
                    try:
                        last_deep = float(self.get_setting("last_deep_scan_ts", 0) or 0)
                    except Exception:
                        last_deep = 0.0
                    deep_scan_allowed = time.time() - last_deep >= DEEP_SCAN_MIN_INTERVAL_S
                if deep_scan_allowed:
                    self._begin_deep_scan()
                    return

            if self._deep_scan_started:
                try:
                    self.set_setting("last_deep_scan_ts", time.time())
                except Exception:
                    pass
            self._set_progress(PROGRESS_FINALIZE, self._s("comparing_versions"))
            self._store_last_results()
            run_on_ui_thread(self._inject_icon_now)
            self._last_scan_exists = True

            if self._silent_mode:
                if updates:
                    run_on_ui_thread(self._show_results_dialog)
            else:
                self._set_progress(100, self._s("done"))
                run_on_ui_thread(self._dismiss_loading_dialog)
                run_on_ui_thread(self._show_results_dialog)

            try:
                self.set_setting("last_check_ts", time.time())
                if self._silent_mode and self._incremental_since == 0:
                    self.set_setting("last_full_scan_ts", time.time())
            except Exception:
                pass
            self._end_check()

        except Exception as e:
            log(f"Error finalizing check: {e}\n{traceback.format_exc()}")
            if not self._silent_mode:
                run_on_ui_thread(self._dismiss_loading_dialog)
                run_on_ui_thread(lambda: BulletinHelper.show_error(self._s("error_comparing")))
            self._end_check()

    def _get_local_plugins(self):
        plugins = {}
        plugins_dir = get_plugins_dir()
        if not plugins_dir or not os.path.isdir(str(plugins_dir)):
            return plugins

        dir_path = str(plugins_dir)
        sources = []
        try:
            for entry in os.listdir(dir_path):
                full = os.path.join(dir_path, entry)
                if not os.path.isfile(full):
                    continue
                if entry.startswith(".") or entry.startswith("_"):
                    continue
                lower = entry.lower()
                if lower.endswith((".plugin", ".py")):
                    sources.append((full, "py"))
                elif lower.endswith((".elyx", ".eaf")):
                    sources.append((full, "elyx"))
        except Exception as e:
            log(f"Error listing plugins_dir: {e}")

        for file_path, kind in sources:
            try:
                meta = None
                if kind == "py":
                    content = self._read_plugin_file(file_path)
                    meta = self._parse_plugin_metadata(content) if content else None
                elif kind == "elyx":
                    meta = self._parse_elyx_file(file_path)
                if meta and meta.get("id"):
                    pid = meta["id"]
                    info = {
                        "name": meta.get("name", pid),
                        "version": meta.get("version", "0"),
                        "path": str(file_path),
                    }
                    existing = plugins.get(pid)
                    if existing is None:
                        plugins[pid] = info
                    else:
                        base = os.path.basename(file_path)
                        if base.endswith(".plugin") or self._version_is_newer(str(info["version"]), str(existing.get("version", ""))):
                            plugins[pid] = info
            except Exception:
                pass
        return plugins

    def _parse_plugin_metadata(self, source):
        meta = {}

        m = re.search(r'''__id__\s*=\s*(?:"|')([^"']+)(?:"|')''', source)
        if m:
            meta["id"] = m.group(1)
        m = re.search(r'''__name__\s*=\s*(?:"|')([^"']+)(?:"|')''', source)
        if m:
            meta["name"] = m.group(1)
        m = re.search(r'''__version__\s*=\s*(?:"|')([^"']+)(?:"|')''', source)
        if m:
            meta["version"] = m.group(1)

        if not meta.get("id"):
            try:
                tree = ast.parse(source)
                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and self._get_ast_value(node.value):
                                val = self._get_ast_value(node.value)
                                if target.id == "__id__" and not meta.get("id"):
                                    meta["id"] = val
                                elif target.id == "__name__" and not meta.get("name"):
                                    meta["name"] = val
                                elif target.id == "__version__" and not meta.get("version"):
                                    meta["version"] = val
            except Exception:
                pass

        return meta

    def _get_ast_value(self, node):
        if isinstance(node, ast.Constant):
            return str(node.value)
        return None

    def _read_plugin_file(self, file_path):
        for enc in ["utf-8", "latin-1"]:
            try:
                with open(file_path, "r", encoding=enc, errors="replace") as f:
                    return f.read()
            except Exception:
                continue
        return None

    def _version_token(self, token):
        m = re.search(r"\d+", token)
        return int(m.group()) if m else None

    def _version_is_newer(self, new_ver, old_ver):
        try:
            new_tokens = [t for t in re.split(r"[._\-+]", str(new_ver)) if t]
            old_tokens = [t for t in re.split(r"[._\-+]", str(old_ver)) if t]
            new_parts = [p for p in (self._version_token(t) for t in new_tokens) if p is not None]
            old_parts = [p for p in (self._version_token(t) for t in old_tokens) if p is not None]
            if not new_parts or not old_parts:
                return str(new_ver) != str(old_ver)
            max_len = max(len(new_parts), len(old_parts))
            while len(new_parts) < max_len:
                new_parts.append(0)
            while len(old_parts) < max_len:
                old_parts.append(0)
            return new_parts > old_parts
        except (ValueError, AttributeError):
            return str(new_ver) != str(old_ver)

    def _get_document_filename(self, doc):
        if not hasattr(doc, "attributes") or not doc.attributes:
            return None
        for j in range(doc.attributes.size()):
            attr = doc.attributes.get(j)
            if isinstance(attr, TLRPC.TL_documentAttributeFilename):
                return attr.file_name
        return None

    def _load_cache(self):
        try:
            if get_cache_dir is None:
                return {"channels": {}}
            cache_dir = get_cache_dir()
            if cache_dir is None:
                return {"channels": {}}
            path = os.path.join(str(cache_dir), CACHE_FILE_NAME)
            if not os.path.isfile(path):
                return {"channels": {}}
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()
            if not raw:
                return {"channels": {}}
            data = json.loads(raw)
            if data.get("version") not in (1, CACHE_VERSION):
                return {"channels": {}}
            if not isinstance(data.get("channels"), dict):
                data["channels"] = {}
            migrated = {}
            for username, files in data["channels"].items():
                if not isinstance(files, dict):
                    continue
                new_files = {}
                for fname, val in files.items():
                    if isinstance(val, dict) and "docs" not in val and val.get("doc_id") is not None:
                        new_files[fname] = {"docs": {str(val.get("doc_id")): {
                            "plugin_id": val.get("plugin_id"),
                            "version": val.get("version"),
                            "name": val.get("name"),
                        }}}
                    else:
                        new_files[fname] = val
                migrated[username] = new_files
            data["channels"] = migrated
            return data
        except Exception:
            return {"channels": {}}

    def _save_cache(self):
        try:
            if get_cache_dir is None:
                return
            cache_dir = get_cache_dir()
            if cache_dir is None:
                return
            cache_dir_path = str(cache_dir)
            try:
                os.makedirs(cache_dir_path, exist_ok=True)
            except Exception:
                pass
            channels = dict(self._cache_data.get("channels", {}))
            for username, entries in self._new_cache_entries.items():
                merged = dict(channels.get(username, {}))
                for fname, entry_cache in entries.items():
                    existing = merged.get(fname)
                    if (isinstance(existing, dict) and isinstance(existing.get("docs"), dict)
                            and isinstance(entry_cache, dict) and isinstance(entry_cache.get("docs"), dict)):
                        combined = dict(existing["docs"])
                        combined.update(entry_cache["docs"])
                        merged[fname] = {"docs": combined}
                    else:
                        merged[fname] = entry_cache
                channels[username] = merged
            payload = {
                "version": CACHE_VERSION,
                "channels": channels,
            }
            with open(os.path.join(cache_dir_path, CACHE_FILE_NAME), "w", encoding="utf-8") as f:
                f.write(json.dumps(payload))
        except Exception:
            pass

    def _get_channels_to_check(self):
        channels = []
        custom = self._get_saved_custom_channels_text()
        if custom:
            normalized = custom.replace("\r", " ").replace("\n", " ")
            for part in re.split(r"[\s,;]+", normalized):
                line = part.strip()
                if not line:
                    continue
                username = self._extract_username_from_url(line)
                if username and username not in channels:
                    channels.append(username)
        return channels

    def _extract_username_from_url(self, text):
        if text.startswith("@"):
            text = text[1:]

        patterns = [
            r'(?:https?://)?(?:t\.me|telegram\.me|telegram\.dog)/([a-zA-Z0-9_]+)',
            r'(?:https?://)?([a-zA-Z0-9_]+)\.(?:t\.me|telegram\.me|telegram\.dog)',
        ]
        for pattern in patterns:
            m = re.search(pattern, text)
            if m:
                return m.group(1)

        if "@" in text:
            text = text.split("@")[-1]

        return text

    def _error_text(self, error, fallback):
        try:
            text = getattr(error, "text", None)
            if text:
                return str(text)
        except Exception:
            pass
        try:
            s = str(error)
            if s and s != "None":
                return s
        except Exception:
            pass
        return fallback

    def _show_loading_dialog(self):
        try:
            fragment = get_last_fragment()
            if not fragment:
                return
            activity = fragment.getParentActivity()
            if not activity:
                return

            def show():
                try:
                    builder = AlertDialogBuilder(activity, AlertDialogBuilder.ALERT_TYPE_LOADING)
                    builder.set_title(self._s("checking_title"))
                    builder.set_neutral_button(self._s("minimize"), lambda bld, w: self._minimize_check(bld))
                    builder.set_negative_button(self._s("cancel"), lambda bld, w: self._cancel_check(bld))
                    msg = getattr(self, "_last_progress_message", None)
                    if msg:
                        try:
                            builder.set_message(msg)
                        except Exception:
                            pass
                    dialog = builder.show()
                    self._loading_dialog = dialog
                    self._loading_builder = builder
                    try:
                        if hasattr(dialog, "set_progress"):
                            dialog.set_progress(self._progress)
                        elif hasattr(dialog, "setProgress"):
                            dialog.setProgress(self._progress)
                        raw = dialog.get_dialog() if hasattr(dialog, "get_dialog") else dialog
                        if raw and hasattr(raw, "setProgress"):
                            raw.setProgress(self._progress)
                    except Exception:
                        pass
                    if msg:
                        try:
                            raw = dialog.get_dialog() if hasattr(dialog, "get_dialog") else dialog
                            if raw and hasattr(raw, "setMessage"):
                                raw.setMessage(msg)
                        except Exception:
                            pass
                    try:
                        dialog.setCancelable(True)
                    except Exception:
                        pass
                except Exception as e:
                    log(f"Error showing loading dialog: {e}")

            run_on_ui_thread(show)
        except Exception as e:
            log(f"Error in _show_loading_dialog: {e}")

    def _minimize_check(self, dialog):
        try:
            dialog.dismiss()
        except Exception:
            pass
        self._loading_dialog = None
        self._loading_builder = None
        BulletinHelper.show_info(self._s("minimized_info"))

    def _cancel_check(self, dialog):
        dialog.dismiss()
        self._loading_dialog = None
        self._end_check()
        BulletinHelper.show_info(self._s("check_cancelled"))

    def _dismiss_loading_dialog(self):
        try:
            if self._loading_dialog:
                self._loading_dialog.dismiss()
            self._loading_dialog = None
            self._loading_builder = None
        except Exception:
            pass

    def _set_progress(self, percent, message, force=False):
        if self._silent_mode:
            return
        try:
            percent = min(int(percent), 100)
            msg_changed = getattr(self, "_last_progress_message", None) != message
            if not force and percent <= self._progress and not msg_changed:
                return
            now = time.time() * 1000.0
            if not force and not msg_changed and percent < 100:
                if self._progress_ts and now - self._progress_ts < PROGRESS_THROTTLE_MS:
                    return
            self._progress_ts = now
            self._progress = percent
            self._last_progress_message = message

            def update():
                try:
                    dlg = self._loading_dialog
                    if dlg:
                        try:
                            if hasattr(dlg, "set_progress"):
                                dlg.set_progress(self._progress)
                            elif hasattr(dlg, "setProgress"):
                                dlg.setProgress(self._progress)
                            raw = dlg.get_dialog() if hasattr(dlg, "get_dialog") else dlg
                            if raw and hasattr(raw, "setProgress"):
                                raw.setProgress(self._progress)
                        except Exception:
                            pass
                        try:
                            raw = dlg.get_dialog() if hasattr(dlg, "get_dialog") else dlg
                            if raw and hasattr(raw, "setMessage"):
                                raw.setMessage(message)
                            elif hasattr(dlg, "set_message"):
                                dlg.set_message(message)
                        except Exception:
                            pass
                except Exception:
                    pass

            run_on_ui_thread(update)
        except Exception:
            pass

    def _get_ignored_map(self):
        try:
            raw = self.get_setting("ignored_updates_json", "")
            if raw:
                data = json.loads(raw)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
        return {}

    def _save_ignored_map(self, ignored):
        try:
            self.set_setting("ignored_updates_json", json.dumps(ignored), reload_settings=True)
        except Exception:
            try:
                self.set_setting("ignored_updates_json", json.dumps(ignored))
            except Exception:
                pass

    def _is_update_ignored(self, pid, version, ignored=None):
        if ignored is None:
            ignored = self._get_ignored_map()
        entry = ignored.get(pid)
        if not isinstance(entry, dict):
            return False
        if entry.get("all"):
            return True
        versions = entry.get("versions")
        return isinstance(versions, list) and str(version) in [str(v) for v in versions]

    def _on_ignore_update(self, entry):
        try:
            fragment = get_last_fragment()
            if not fragment:
                return
            activity = fragment.getParentActivity()
            if not activity:
                return
            builder = AlertDialogBuilder(activity)
            builder.set_title(self._s("ignore_this_version"))
            builder.set_message(self._s("ignore_question"))
            builder.set_positive_button(self._s("ignore_all_versions"), lambda bld, w: self._apply_ignore(entry, True, bld))
            builder.set_neutral_button(self._s("ignore_this_version"), lambda bld, w: self._apply_ignore(entry, False, bld))
            builder.set_negative_button(self._s("cancel"), lambda bld, w: bld.dismiss())
            builder.show()
        except Exception as e:
            log(f"Error showing ignore dialog: {e}")

    def _dismiss_results_dialog(self):
        try:
            dlg = self._results_dialog_holder.get("dialog")
            if dlg is not None:
                dlg.dismiss()
        except Exception:
            pass
        self._results_dialog_holder["dialog"] = None

    def _ignore_plugin(self, pid, version=None, all_versions=False):
        if not pid:
            return
        ignored = self._get_ignored_map()
        slot = ignored.get(pid)
        if not isinstance(slot, dict):
            slot = {}
            ignored[pid] = slot
        if all_versions or not version:
            slot["all"] = True
        else:
            versions = slot.get("versions")
            if not isinstance(versions, list):
                versions = []
                slot["versions"] = versions
            if str(version) not in [str(v) for v in versions]:
                versions.append(str(version))
        self._save_ignored_map(ignored)

    def _apply_ignore(self, entry, all_versions, confirm_dialog=None):
        try:
            if confirm_dialog is not None:
                try:
                    confirm_dialog.dismiss()
                except Exception:
                    pass
            self._dismiss_results_dialog()
            pid = entry.get("plugin_id")
            self._ignore_plugin(pid, entry.get("channel_version"), all_versions)
            self._updates = [
                u for u in self._updates
                if not (u.get("plugin_id") == pid and (all_versions or u.get("channel_version") == entry.get("channel_version")))
            ]
            self._store_last_results()
            BulletinHelper.show_info(self._s("ignored_bulletin"))
            run_on_ui_thread(self._inject_icon_now)
            run_on_ui_thread(self._show_results_dialog)
        except Exception as e:
            log(f"Error applying ignore: {e}")

    def _ignored_summary(self):
        try:
            count = len(self._get_ignored_map())
            if count:
                return self._s("ignored_summary", count)
        except Exception:
            pass
        return self._s("ignored_none")

    def _on_manage_ignored(self, view=None):
        try:
            fragment = get_last_fragment()
            if not fragment:
                return
            activity = fragment.getParentActivity()
            if not activity:
                return
            self._build_ignored_manager(activity)
        except Exception as e:
            log(f"Error opening ignored manager: {e}")

    def _ignored_scope_text(self, pid, slot):
        try:
            if slot.get("all"):
                return self._s("ignored_all_label")
            versions = slot.get("versions")
            if isinstance(versions, list) and versions:
                return self._s("ignored_versions_label", ", ".join(str(v) for v in versions))
        except Exception:
            pass
        return ""

    def _build_ignored_manager(self, activity, dialog_holder=None):
        try:
            from android.widget import LinearLayout, ScrollView, TextView
            from android.graphics import Typeface

            if dialog_holder is None:
                dialog_holder = self._results_dialog_holder

            root = LinearLayout(activity)
            root.setOrientation(LinearLayout.VERTICAL)
            pad = self._dp(16)
            root.setPadding(pad, pad // 2, pad, pad // 2)

            scr = ScrollView(activity)
            list_layout = LinearLayout(activity)
            list_layout.setOrientation(LinearLayout.VERTICAL)
            scr.addView(list_layout)
            root.addView(scr)

            ignored = self._get_ignored_map()
            items = sorted(ignored.items())

            if not items:
                empty = TextView(activity)
                try:
                    empty.setText(self._s("ignored_empty_list"))
                    empty.setTextSize(14.0)
                    empty.setTextColor(self._theme_color("key_dialogTextGray", 0xFF8A8A8A))
                    empty.setPadding(0, self._dp(8), 0, self._dp(8))
                except Exception:
                    pass
                list_layout.addView(empty)

            for pid, slot in items:
                if not isinstance(slot, dict):
                    continue
                row = LinearLayout(activity)
                row.setOrientation(LinearLayout.HORIZONTAL)
                try:
                    left = LinearLayout(activity)
                    left.setOrientation(LinearLayout.VERTICAL)
                    pid_view = TextView(activity)
                    pid_view.setText(str(pid))
                    pid_view.setTextSize(15.0)
                    pid_view.setTextColor(self._theme_color("key_dialogTextBlack", 0xFF1C1C1C))
                    pid_view.setTypeface(None, Typeface.BOLD)
                    left.addView(pid_view)
                    scope = self._ignored_scope_text(pid, slot)
                    if scope:
                        scope_view = TextView(activity)
                        scope_view.setText(scope)
                        scope_view.setTextSize(13.0)
                        scope_view.setTextColor(self._theme_color("key_dialogTextGray", 0xFF8A8A8A))
                        left.addView(scope_view)
                    try:
                        left_params = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0)
                    except Exception:
                        left_params = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT)
                        try:
                            left_params.weight = 1.0
                        except Exception:
                            pass
                    row.addView(left, left_params)
                except Exception:
                    pass
                try:
                    remove = TextView(activity)
                    remove.setText("\u274C")
                    remove.setTextSize(14.0)
                    remove.setPadding(self._dp(8), 0, 0, 0)
                    remove.setOnClickListener(OnClickListener(lambda v, p=pid: self._remove_ignored(p)))
                    row.addView(remove)
                except Exception:
                    pass
                list_layout.addView(row)

            add = TextView(activity)
            try:
                add.setText("+ " + self._s("ignored_add"))
                add.setTextSize(15.0)
                add.setTextColor(self._theme_color("key_dialogTextLink", 0xFF2F8CE0))
                add.setPadding(0, self._dp(12), 0, self._dp(4))
                add.setOnClickListener(OnClickListener(lambda v: self._on_add_ignored()))
            except Exception:
                pass
            list_layout.addView(add)

            builder = AlertDialogBuilder(activity)
            builder.set_title(self._s("ignored_title"))
            builder.set_view(root)
            builder.set_negative_button(self._s("close"), lambda bld, w: bld.dismiss())
            dialog = builder.show()
            dialog_holder["dialog"] = dialog
            return dialog
        except Exception as e:
            log(f"Error building ignored manager: {e}\n{traceback.format_exc()}")
            return None

    def _remove_ignored(self, pid):
        try:
            ignored = self._get_ignored_map()
            if pid in ignored:
                del ignored[pid]
                self._save_ignored_map(ignored)
            self._dismiss_results_dialog()
            self._on_manage_ignored()
        except Exception as e:
            log(f"Error removing ignored plugin: {e}")

    def _on_add_ignored(self):
        try:
            self._dismiss_results_dialog()
            fragment = get_last_fragment()
            if not fragment:
                return
            activity = fragment.getParentActivity()
            if not activity:
                return

            local = self._get_local_plugins()
            if not local:
                BulletinHelper.show_info(self._s("ignored_no_plugins"))
                return

            from android.widget import LinearLayout, ScrollView, TextView
            from android.graphics import Typeface

            root = LinearLayout(activity)
            root.setOrientation(LinearLayout.VERTICAL)
            pad = self._dp(16)
            root.setPadding(pad, pad // 2, pad, pad // 2)

            hint = TextView(activity)
            try:
                hint.setText(self._s("ignored_pick_hint"))
                hint.setTextSize(14.0)
                hint.setTextColor(self._theme_color("key_dialogTextGray", 0xFF8A8A8A))
                hint.setPadding(0, self._dp(4), 0, self._dp(8))
            except Exception:
                pass
            root.addView(hint)

            scr = ScrollView(activity)
            lay = LinearLayout(activity)
            lay.setOrientation(LinearLayout.VERTICAL)
            scr.addView(lay)
            root.addView(scr)

            for pid in sorted(local.keys(), key=lambda p: str(local[p].get("name") or p).lower()):
                info = local[pid]
                row = LinearLayout(activity)
                row.setOrientation(LinearLayout.VERTICAL)
                try:
                    row.setPadding(0, self._dp(8), 0, self._dp(8))
                    name_view = TextView(activity)
                    name_view.setText(str(info.get("name") or pid))
                    name_view.setTextSize(15.0)
                    name_view.setTextColor(self._theme_color("key_dialogTextBlack", 0xFF1C1C1C))
                    name_view.setTypeface(None, Typeface.BOLD)
                    row.addView(name_view)
                    sub_view = TextView(activity)
                    sub_view.setText(str(pid) + " \u00b7 v" + str(info.get("version", "")))
                    sub_view.setTextSize(13.0)
                    sub_view.setTextColor(self._theme_color("key_dialogTextGray", 0xFF8A8A8A))
                    row.addView(sub_view)
                    row.setOnClickListener(OnClickListener(lambda v, e={
                        "plugin_id": pid,
                        "name": info.get("name") or pid,
                        "channel_version": info.get("version"),
                    }: self._on_ignore_installed(e)))
                except Exception:
                    pass
                lay.addView(row)

            builder = AlertDialogBuilder(activity)
            builder.set_title(self._s("ignored_pick_title"))
            builder.set_view(root)
            builder.set_negative_button(self._s("cancel"), lambda bld, w: bld.dismiss())
            dialog = builder.show()
            self._results_dialog_holder["dialog"] = dialog
        except Exception as e:
            log(f"Error showing ignored picker: {e}")

    def _on_ignore_installed(self, entry):
        try:
            fragment = get_last_fragment()
            if not fragment:
                return
            activity = fragment.getParentActivity()
            if not activity:
                return
            builder = AlertDialogBuilder(activity)
            builder.set_title(str(entry.get("name") or entry.get("plugin_id") or ""))
            builder.set_message(self._s("ignore_question"))
            builder.set_positive_button(self._s("ignore_all_versions"), lambda bld, w: self._apply_ignore_installed(entry, True, bld))
            builder.set_neutral_button(self._s("ignore_this_version"), lambda bld, w: self._apply_ignore_installed(entry, False, bld))
            builder.set_negative_button(self._s("cancel"), lambda bld, w: bld.dismiss())
            builder.show()
        except Exception as e:
            log(f"Error showing installed ignore dialog: {e}")

    def _apply_ignore_installed(self, entry, all_versions, confirm_dialog=None):
        try:
            if confirm_dialog is not None:
                try:
                    confirm_dialog.dismiss()
                except Exception:
                    pass
            self._ignore_plugin(entry.get("plugin_id"), entry.get("channel_version"), all_versions)
            BulletinHelper.show_info(self._s("ignored_saved"))
            self._on_manage_ignored()
        except Exception as e:
            log(f"Error applying installed ignore: {e}")

    def _theme_color(self, key_name, fallback):
        try:
            if Theme is not None:
                key = getattr(Theme, key_name, None)
                if key is not None:
                    return Theme.getColor(key)
        except Exception:
            pass
        return fallback

    def _show_results_dialog(self):
        try:
            fragment = get_last_fragment()
            if not fragment:
                self._show_fallback_results()
                return

            activity = fragment.getParentActivity()
            if not activity:
                self._show_fallback_results()
                return

            if self._updates:
                try:
                    local = self._get_local_plugins()
                    kept = []
                    changed = False
                    for u in self._updates:
                        pid = u.get("plugin_id")
                        li = local.get(pid)
                        if li is None or not self._version_is_newer(str(u.get("channel_version", "")), str(li.get("version", ""))):
                            changed = True
                            continue
                        kept.append(u)
                    if changed:
                        self._updates = kept
                        self._store_last_results()
                        self._update_actionbar_icon()
                except Exception:
                    pass

            updates = self._updates
            up_to_date = self._up_to_date
            not_found = self._not_found

            if not updates and not up_to_date and not not_found:
                self._show_simple_result(self._s("no_plugins_to_check"))
                return

            self._build_results_dialog(activity, updates, up_to_date, not_found)

        except Exception as e:
            log(f"Error showing results dialog: {e}\n{traceback.format_exc()}")
            self._show_fallback_results()

    def _build_results_dialog(self, activity, updates, up_to_date, not_found):
        try:
            from android.widget import LinearLayout, TextView
            from android.graphics import Typeface

            root = LinearLayout(activity)
            root.setOrientation(LinearLayout.VERTICAL)
            pad = self._dp(16)
            root.setPadding(pad, pad // 2, pad, pad // 2)

            tabs_row = LinearLayout(activity)
            tabs_row.setOrientation(LinearLayout.HORIZONTAL)
            root.addView(tabs_row)

            content_holder = LinearLayout(activity)
            content_holder.setOrientation(LinearLayout.VERTICAL)
            root.addView(content_holder)

            tabs = [
                ("\U0001F504\uFE0F", updates, "tab_updates"),
                ("\u2754", not_found, "tab_not_found"),
                ("\u2705", up_to_date, "tab_up_to_date"),
            ]
            tab_views = []
            state = {"index": 0}

            def select(index):
                state["index"] = index
                for i, tv in enumerate(tab_views):
                    active = i == index
                    try:
                        tv.setTextColor(self._theme_color(
                            "key_dialogTextLink" if active else "key_dialogTextGray",
                            0xFF2F8CE0 if active else 0xFF8A8A8A))
                        tv.setTypeface(None, Typeface.BOLD if active else Typeface.NORMAL)
                    except Exception:
                        pass
                try:
                    content_holder.removeAllViews()
                    content_holder.addView(self._make_results_page(activity, index, tabs, select_ignore=self._on_ignore_update, open_entry=self._open_results_entry))
                except Exception as e:
                    log(f"Error building results page: {e}")

            for index, (emoji, entries, key) in enumerate(tabs):
                tv = TextView(activity)
                try:
                    tv.setText(f"{emoji} {len(entries)}")
                    tv.setTextSize(16.0)
                    tv.setPadding(self._dp(10), self._dp(8), self._dp(10), self._dp(8))
                    tv.setOnClickListener(OnClickListener(lambda v, i=index: select(i)))
                except Exception:
                    pass
                tab_views.append(tv)
                tabs_row.addView(tv)

            select(0)

            builder = AlertDialogBuilder(activity)
            builder.set_title(self._s("results_title"))
            builder.set_view(root)
            builder.set_negative_button(self._s("close"), lambda bld, w: bld.dismiss())
            dialog = builder.show()
            self._results_dialog_holder["dialog"] = dialog
            return dialog
        except Exception as e:
            log(f"Error building results dialog: {e}\n{traceback.format_exc()}")
            self._show_fallback_results()

    def _open_results_entry(self, entry):
        self._dismiss_results_dialog()
        self._open_card_message(entry)

    def _open_card_message(self, entry):
        try:
            channel_id = entry.get("channel_id")
            message_id = entry.get("message_id")
            if channel_id is None or message_id is None:
                BulletinHelper.show_info(self._s("not_found_hint"))
                return
            self._open_message(channel_id, message_id)
        except Exception as e:
            log(f"Error opening card message: {e}")

    def _make_results_page(self, activity, index, tabs, select_ignore=None, open_entry=None):
        try:
            from android.widget import LinearLayout, ScrollView, TextView
            from android.graphics import Typeface

            emoji, entries, key = tabs[index]
            holder = ScrollView(activity)
            list_layout = LinearLayout(activity)
            list_layout.setOrientation(LinearLayout.VERTICAL)
            holder.addView(list_layout)

            desc = TextView(activity)
            try:
                desc.setText(self._s(key + "_desc" if entries else key + "_empty"))
                desc.setTextSize(14.0)
                desc.setPadding(self._dp(8), self._dp(10), self._dp(8), self._dp(4))
                desc.setTextColor(self._theme_color("key_dialogTextGray", 0xFF8A8A8A))
            except Exception:
                pass
            list_layout.addView(desc)

            if not entries:
                return holder

            for entry in entries:
                try:
                    list_layout.addView(self._make_plugin_card(activity, key, entry, select_ignore, open_entry))
                except Exception as e:
                    log(f"Error building card: {e}")
            return holder
        except Exception as e:
            log(f"Error making results page: {e}")
            try:
                from android.widget import LinearLayout
                empty_layout = LinearLayout(activity)
                return empty_layout
            except Exception:
                return None

    def _make_plugin_card(self, activity, kind, entry, select_ignore, open_entry):
        from android.widget import LinearLayout, TextView
        from android.graphics import Typeface

        card = LinearLayout(activity)
        card.setOrientation(LinearLayout.VERTICAL)
        try:
            bg = GradientDrawable()
            bg.setShape(GradientDrawable.RECTANGLE)
            bg.setCornerRadius(self._dp(12))
            bg.setColor(self._theme_color("key_dialogBackground", 0xFFFFFFFF))
            try:
                bg.setStroke(self._dp(1), self._theme_color("key_dialogBackgroundGray", 0xFFE0E0E0))
            except Exception:
                pass
            card.setBackground(bg)
        except Exception:
            pass
        card.setPadding(self._dp(12), self._dp(10), self._dp(12), self._dp(10))

        from android.widget import LinearLayout as _LL

        header_row = LinearLayout(activity)
        header_row.setOrientation(_LL.HORIZONTAL)

        left_col = LinearLayout(activity)
        left_col.setOrientation(_LL.VERTICAL)

        title_row = left_col

        name_view = TextView(activity)
        try:
            name_view.setText(str(entry.get("name") or entry.get("plugin_id") or "?"))
            name_view.setTextSize(16.0)
            name_view.setTextColor(self._theme_color("key_dialogTextBlack", 0xFF1C1C1C))
            name_view.setTypeface(None, Typeface.BOLD)
        except Exception:
            pass

        meta_text = ""
        clickable = False
        if kind == "tab_updates":
            try:
                meta_text = self._s("version_same_line", entry.get("local_version", "?"), entry.get("channel_version", "?"))
                suffix = self._s("channel_suffix", entry.get("channel_username", ""))
                if suffix and suffix != "@":
                    meta_text += "  " + suffix
                clickable = True
            except Exception:
                meta_text = ""
        elif kind == "tab_up_to_date":
            try:
                meta_text = str(entry.get("version", ""))
                suffix = self._s("channel_suffix", entry.get("channel_username", ""))
                if suffix and suffix != "@":
                    meta_text += "  " + suffix
                clickable = True
            except Exception:
                meta_text = ""

        try:
            title_row.addView(name_view)
        except Exception:
            pass

        meta_view = TextView(activity)
        try:
            meta_view.setText(meta_text)
            meta_view.setTextSize(14.0)
            meta_view.setTextColor(self._theme_color("key_dialogTextGray", 0xFF8A8A8A))
            left_col.addView(meta_view)
        except Exception:
            pass

        cross = None
        if kind == "tab_updates" and select_ignore is not None:
            try:
                cross = TextView(activity)
                cross.setText("\u274C")
                cross.setTextSize(14.0)
                cross.setPadding(self._dp(8), 0, 0, 0)
                cross.setOnClickListener(OnClickListener(lambda v, e=entry: select_ignore(e)))
            except Exception:
                cross = None

        try:
            try:
                left_params = _LL.LayoutParams(0, _LL.LayoutParams.WRAP_CONTENT, 1.0)
            except Exception:
                left_params = _LL.LayoutParams(_LL.LayoutParams.MATCH_PARENT, _LL.LayoutParams.WRAP_CONTENT)
                try:
                    left_params.weight = 1.0
                except Exception:
                    pass
            header_row.addView(left_col, left_params)
        except Exception:
            header_row.addView(left_col)
        if cross is not None:
            try:
                cross_params = _LL.LayoutParams(_LL.LayoutParams.WRAP_CONTENT, _LL.LayoutParams.WRAP_CONTENT)
                try:
                    cross_params.gravity = 16  # CENTER_VERTICAL
                except Exception:
                    pass
                header_row.addView(cross, cross_params)
            except Exception:
                header_row.addView(cross)
        card.addView(header_row)

        try:
            if clickable and open_entry is not None:
                card.setOnClickListener(OnClickListener(lambda v, e=entry: open_entry(e)))
        except Exception:
            pass

        try:
            from android.widget import LinearLayout as _LL
            params = _LL.LayoutParams(_LL.LayoutParams.MATCH_PARENT, _LL.LayoutParams.WRAP_CONTENT)
            margin = self._dp(6)
            try:
                params.setMargins(margin, margin // 2, margin, margin // 2)
            except Exception:
                pass
            card.setLayoutParams(params)
        except Exception:
            pass

        return card

    def _open_message(self, channel_id, message_id):
        try:
            fragment = get_last_fragment()
            if not fragment:
                return

            bundle = Bundle()
            bundle.putLong("chat_id", channel_id)
            bundle.putInt("message_id", message_id)

            chat_activity = ChatActivity(bundle)
            fragment.presentFragment(chat_activity)

        except Exception as e:
            log(f"Error opening message: {e}\n{traceback.format_exc()}")
            BulletinHelper.show_error(self._s("failed_open"))

    def _show_fallback_results(self):
        try:
            updates = getattr(self, "_updates", [])
            up_to_date = getattr(self, "_up_to_date", [])
            not_found = getattr(self, "_not_found", [])

            parts = []

            if updates:
                lines = [self._s("updates_header", len(updates))]
                for u in updates:
                    lines.append(self._s("update_line", u['name']))
                    lines.append(self._s("version_line", u['local_version'], u['channel_version'], u['channel_username']))
                parts.append("\n".join(lines))

            if up_to_date:
                parts.append(self._s("up_to_date_header", len(up_to_date)))

            if not_found:
                lines = [self._s("not_found_header", len(not_found))]
                for n in not_found:
                    name = n.get("name") if isinstance(n, dict) else n
                    lines.append(self._s("not_found_item", name))
                parts.append("\n".join(lines))

            if not parts:
                msg = self._s("no_plugins_to_check")
            else:
                msg = "\n\n".join(parts)

            self._show_simple_result(msg)
        except Exception as e:
            log(f"Error in fallback results: {e}")
            BulletinHelper.show_info(self._s("check_complete"))

    def _show_simple_result(self, message):
        try:
            fragment = get_last_fragment()
            if not fragment:
                BulletinHelper.show_info(str(message)[:100])
                return

            activity = fragment.getParentActivity()
            if not activity:
                BulletinHelper.show_info(str(message)[:100])
                return

            builder = AlertDialogBuilder(activity)
            builder.set_title(self._s("plugin_name"))
            builder.set_message(str(message))
            builder.set_positive_button(self._s("ok"), lambda bld, w: bld.dismiss())
            builder.show()
        except Exception as e:
            log(f"Error showing result dialog: {e}")
            BulletinHelper.show_info(str(message)[:100])

# __DEX_BEGIN__
# PLACEHOLDER
# __DEX_END__
