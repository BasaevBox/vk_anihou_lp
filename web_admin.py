"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    WEB ADMIN PANEL v5.0 — FULL EDITION                       ║
║                              Админ-панель                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import threading
import json
import os
import time
import re
from datetime import datetime
from typing import TYPE_CHECKING
from flask import Flask, render_template_string, request, jsonify
from utils import log

if TYPE_CHECKING:
    from bot import VKBot

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>AniHou | Админ панель</title>
<style>
:root{--bg1:#1a0f2e;--bg2:#0d0b1f;--card:#16122b;--accent1:#ff6b6b;--accent2:#ff8e53;--text:#e0e0e0;--muted:#8888a0;--online:#4ade80;}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{background:linear-gradient(180deg,var(--bg1) 0%,var(--bg2) 100%);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:var(--text);min-height:100vh;padding-bottom:80px}
.container{max-width:900px;margin:0 auto;padding:12px}

.top-bar{display:flex;align-items:center;gap:10px;margin-bottom:16px;padding:8px 4px}
.search-wrap{flex:1;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);border-radius:24px;display:flex;align-items:center;padding:8px 14px;gap:8px}
.search-wrap input{background:transparent;border:none;outline:none;color:var(--text);font-size:15px;width:100%}
.search-wrap span{color:var(--muted);font-size:18px}
.top-icon{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);display:flex;align-items:center;justify-content:center;font-size:16px;color:var(--text)}
.avatar-top{width:36px;height:36px;border-radius:50%;overflow:hidden;border:2px solid rgba(255,255,255,0.15);position:relative}
.avatar-top img{width:100%;height:100%;object-fit:cover}
.avatar-top::after{content:"";position:absolute;bottom:0;right:0;width:10px;height:10px;background:var(--online);border-radius:50%;border:2px solid var(--bg1)}

.profile-card{background:linear-gradient(180deg,#2d1b4e 0%,#1a1033 100%);border-radius:24px;overflow:hidden;margin-bottom:20px;box-shadow:0 8px 32px rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.05)}
.cover{height:160px;background:linear-gradient(135deg,#4a2c7a 0%,#2d1b4e 100%);display:flex;align-items:center;justify-content:center;position:relative}
.cover-icon{font-size:48px;opacity:0.25}
.avatar-wrap{position:relative;margin-top:-55px;margin-left:20px;display:inline-block}
.avatar{width:110px;height:110px;border-radius:50%;border:4px solid #1a1033;background:linear-gradient(135deg,#ff6b6b,#ff8e53);display:flex;align-items:center;justify-content:center;font-size:42px;box-shadow:0 4px 20px rgba(0,0,0,0.3);overflow:hidden}
.avatar img{width:100%;height:100%;object-fit:cover;border-radius:50%}
.online-dot{position:absolute;bottom:8px;right:8px;width:18px;height:18px;background:var(--online);border-radius:50%;border:3px solid #1a1033}
.profile-body{padding:12px 20px 20px}
.profile-name{font-size:26px;font-weight:700;color:#fff;display:flex;align-items:center;gap:8px}
.crown{font-size:22px}
.profile-bio{color:#a0a0b0;font-size:15px;margin-top:6px;line-height:1.4}
.profile-meta{display:flex;gap:20px;margin-top:14px;flex-wrap:wrap}
.meta-item{display:flex;align-items:center;gap:6px;color:#8888a0;font-size:14px}
.edit-btn{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);color:#60a5fa;padding:8px 18px;border-radius:20px;cursor:pointer;font-size:14px;margin-top:14px;transition:all .2s}
.edit-btn:hover{background:rgba(255,255,255,0.15)}

/* === ТАБЫ === */
.tabs{display:flex;gap:8px;margin-bottom:16px;overflow-x:auto;padding-bottom:4px;scrollbar-width:none}
.tabs::-webkit-scrollbar{display:none}
.tab{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);color:var(--muted);padding:8px 14px;border-radius:16px;cursor:pointer;font-size:13px;white-space:nowrap;transition:all .2s;border:none;outline:none;font-family:inherit}
.tab.active{background:linear-gradient(135deg,var(--accent1),var(--accent2));color:#fff;font-weight:600;border-color:transparent}
.tab:hover:not(.active){background:rgba(255,255,255,0.1);color:#ccc}

/* === КАРТОЧКИ === */
.card{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);border-radius:20px;padding:18px;margin-bottom:14px;backdrop-filter:blur(10px)}
.card-title{font-size:17px;font-weight:600;color:#fff;margin-bottom:14px;display:flex;align-items:center;gap:8px}
.card-subtitle{font-size:13px;color:var(--accent1);margin-bottom:10px}

/* === ФОРМЫ === */
.form-group{margin-bottom:14px}
.form-group label{display:block;margin-bottom:6px;font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
input,select,textarea{width:100%;padding:10px 12px;background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.1);border-radius:14px;color:var(--text);font-size:14px;transition:all .2s;font-family:inherit}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--accent1);background:rgba(0,0,0,0.4)}
textarea{min-height:70px;resize:vertical}

/* === КНОПКИ === */
.btn{background:linear-gradient(135deg,var(--accent1),var(--accent2));color:#fff;border:none;padding:8px 16px;border-radius:12px;cursor:pointer;font-size:13px;font-weight:500;transition:all .2s;display:inline-flex;align-items:center;gap:6px;font-family:inherit}
.btn:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(255,107,107,0.3)}
.btn-secondary{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);color:var(--text)}
.btn-secondary:hover{background:rgba(255,255,255,0.15)}
.btn-danger{background:#dc3545}
.btn-success{background:#28a745}
.btn-sm{padding:5px 10px;font-size:12px}
.flex{display:flex;gap:10px;flex-wrap:wrap}.flex-col{flex-direction:column}.mt-2{margin-top:8px}.w-full{width:100%}

/* === СЕТКА === */
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:768px){
 .grid-2{grid-template-columns:1fr}
 .profile-name{font-size:22px}
 .avatar{width:90px;height:90px;font-size:36px}
 .avatar-wrap{margin-top:-45px;margin-left:16px}
 .tabs{gap:6px}
 .tab{padding:7px 12px;font-size:12px}
}

/* === ТАБЛИЦЫ === */
.table-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:10px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.06)}
th{color:var(--accent1);font-weight:600;font-size:12px;text-transform:uppercase}
td{color:#c0c0d0}
tr:hover td{background:rgba(255,255,255,0.02)}
.badge{display:inline-block;padding:3px 8px;border-radius:20px;font-size:11px;font-weight:500}
.badge-green{background:rgba(74,222,128,0.15);color:#4ade80}
.badge-red{background:rgba(248,113,113,0.15);color:#f87171}
.badge-blue{background:rgba(96,165,250,0.15);color:#60a5fa}

/* === НИЖНЯЯ НАВИГАЦИЯ (Android style) === */
.bottom-nav{position:fixed;bottom:0;left:0;right:0;height:56px;background:rgba(13,11,31,0.95);backdrop-filter:blur(12px);border-top:1px solid rgba(255,255,255,0.06);display:flex;align-items:center;justify-content:space-around;z-index:100}
.nav-btn{color:var(--muted);background:none;border:none;font-size:22px;cursor:pointer;padding:8px 16px}
.nav-btn.active{color:#fff}

/* === РЕДАКТОР === */
.editor-area{width:100%;min-height:300px;font-family:"Consolas","Monaco",monospace;font-size:13px;line-height:1.5;background:rgba(0,0,0,0.4);color:#fff;padding:12px;border-radius:14px;border:1px solid rgba(255,255,255,0.1);resize:vertical;white-space:pre;tab-size:4}
.file-list{display:flex;flex-direction:column;gap:6px}
.file-item{padding:10px 12px;background:rgba(255,255,255,0.04);border-radius:12px;cursor:pointer;display:flex;align-items:center;justify-content:space-between;transition:all .2s;border:1px solid transparent}
.file-item:hover{background:rgba(255,255,255,0.08);border-color:rgba(255,255,255,0.1)}
.file-item.active{background:rgba(255,107,107,0.1);border-color:rgba(255,107,107,0.3);color:var(--accent1)}

/* === ТОСТ === */
.toast{position:fixed;bottom:70px;left:50%;transform:translateX(-50%);padding:12px 20px;border-radius:16px;color:#fff;font-size:14px;z-index:9999;animation:fadeIn .3s ease;max-width:90vw;word-break:break-word;text-align:center}
.toast-success{background:linear-gradient(135deg,#22c55e,#16a34a)}
.toast-error{background:linear-gradient(135deg,#ef4444,#dc2626)}
@keyframes fadeIn{from{opacity:0;transform:translateX(-50%) translateY(10px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}

.hidden{display:none!important}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-thumb{background:rgba(255,107,107,0.4);border-radius:3px}
</style>
</head>
<body>
<div class="container">

<!-- ПРОФИЛЬ -->
<div class="profile-card">
  <div class="cover"><div class="cover-icon">хуй</div></div>
  <div class="avatar-wrap">
    <div class="avatar"><img src="https://api.dicebear.com/7.x/bottts/svg?seed=AniHou" alt="avatar" style="width:100%;height:100%"></div>
    <div class="online-dot"></div>
  </div>
  <div class="profile-body">
    <div class="profile-name">для андрея <span class="crown">👑</span></div>
    <div class="profile-bio">модуль создан для упрощения управления ботом</div>
    <div class="profile-meta">
      <div class="meta-item">📍 Russia</div>
      <div class="meta-item">🔗 {{ bot_url }}</div>
      <div class="meta-item">📅 Joined {{ start_date }}</div>
    </div>
    <button class="edit-btn" onclick="showToast('не заслужил')">✏️ Edit</button>
  </div>
</div>

<!-- ТАБЫ -->
<div class="tabs">
  <button class="tab active" onclick="switchTab('dashboard')">📊 Главная</button>
  <button class="tab" onclick="switchTab('commands')">💬 Команды</button>
  <button class="tab" onclick="switchTab('modules')">🧩 Модули</button>
  <button class="tab" onclick="switchTab('trusted')">🔒 Доверенные</button>
  <button class="tab" onclick="switchTab('settings')">⚙️ Настройки</button>
  <button class="tab" onclick="switchTab('autopost')">📢 Автопост</button>
  <button class="tab" onclick="switchTab('editor')">📝 Редактор</button>
  <button class="tab" onclick="switchTab('constructor')">🚀 Конструктор</button>
</div>

<!-- ====== ДАШБОРД ====== -->
<div id="dashboard" class="tab-content">
  <div class="grid-2">
    <div class="card">
      <div class="card-title">📊 Статус бота</div>
      <div class="form-group"><label>Состояние</label><span class="badge badge-green" id="bot-status-badge">🟢 Онлайн</span></div>
      <div class="form-group"><label>Аптайм</label><div id="uptime" style="font-size:20px;font-weight:700">--</div></div>
      <div class="form-group"><label>Всего команд</label><div id="total-commands" style="font-size:20px;font-weight:700">0</div></div>
    </div>
    <div class="card">
      <div class="card-title">🎨 Автостатус</div>
      <div class="form-group"><label>Анимация</label><select id="animation-select" onchange="changeAnimation()"><option value="wave">Волна</option><option value="pulse">Пульс</option><option value="clock">Часы</option><option value="moon">Луна</option><option value="loading">Загрузка</option><option value="matrix">Матрица</option><option value="typing">Печатает</option><option value="equalizer">Эквалайзер</option><option value="bounce">Прыжок</option></select></div>
      <div class="form-group"><label>Автостатус</label><button id="toggle-status-btn" class="btn btn-secondary" onclick="toggleAutoStatus()">Включить</button></div>
    </div>
  </div>
  <div class="card">
    <div class="card-title">📝 Статистика</div>
    <div class="grid-2">
      <div class="form-group"><label>Доверенных</label><div id="trusted-count" style="font-size:22px;font-weight:700;color:#60a5fa">0</div></div>
      <div class="form-group"><label>Кастомных команд</label><div id="custom-count" style="font-size:22px;font-weight:700;color:#fbbf24">0</div></div>
      <div class="form-group"><label>RP команд</label><div id="rp-count" style="font-size:22px;font-weight:700;color:#a78bfa">0</div></div>
      <div class="form-group"><label>Анимаций</label><div id="anim-count" style="font-size:22px;font-weight:700;color:#f472b6">0</div></div>
    </div>
  </div>
</div>

<!-- ====== КОМАНДЫ ====== -->
<div id="commands" class="tab-content hidden">
  <div class="card">
    <div class="card-title">➕ Создать команду</div>
    <div class="form-group"><label>Название (без !)</label><input type="text" id="cmd-name" placeholder="привет"></div>
    <div class="form-group"><label>Описание</label><input type="text" id="cmd-desc" placeholder="Краткое описание"></div>
    <div class="form-group"><label>Ответ бота</label><textarea id="cmd-response" placeholder="Привет, {user}!"></textarea></div>
    <button class="btn" onclick="createCommand()">✨ Создать</button>
  </div>
  <div class="card">
    <div class="card-title">📋 Кастомные команды</div>
    <div class="table-wrap"><table><thead><tr><th>Команда</th><th>Описание</th><th></th></tr></thead><tbody id="commands-list"></tbody></table></div>
  </div>
</div>

<!-- ====== МОДУЛИ ====== -->
<div id="modules" class="tab-content hidden">
  <div class="grid-2">
    <div class="card">
      <div class="card-title">🎭 RP Команды</div>
      <div class="form-group"><label>Название</label><input type="text" id="rp-name" placeholder="обнять"></div>
      <div class="form-group"><label>Текст</label><input type="text" id="rp-text" placeholder="обнял(а)"></div>
      <div class="form-group"><label>Эмодзи</label><input type="text" id="rp-emoji" placeholder="🤗"></div>
      <button class="btn" onclick="addRPCommand()">➕ Добавить</button>
      <div class="table-wrap mt-2"><table><thead><tr><th>Команда</th><th>Эмодзи</th><th>Текст</th><th></th></tr></thead><tbody id="rp-list"></tbody></table></div>
    </div>
    <div class="card">
      <div class="card-title">🎨 Anime API</div>
      <div class="form-group"><label>NSFW режим</label><select id="nsfw-mode" onchange="saveAnimeSettings()"><option value="false">👶 Выключен</option><option value="true">🔞 Включен</option></select></div>
      <div class="form-group"><label>SFW группы (ID через запятую)</label><textarea id="sfw-groups" rows="2" placeholder="-89528768, -210485938"></textarea></div>
      <div class="form-group"><label>NSFW группы</label><textarea id="nsfw-groups" rows="2" placeholder="-101072212"></textarea></div>
      <button class="btn" onclick="saveAnimeSettings()">💾 Сохранить</button>
    </div>
  </div>
  <div class="card">
    <div class="card-title">📢 Автопостинг</div>
    <div class="grid-2">
      <div class="form-group"><label>Статус</label><button id="autopost-toggle-btn" class="btn btn-secondary" onclick="toggleAutoPost()">Включить</button></div>
      <div class="form-group"><label>ID группы</label><input type="text" id="autopost-group" placeholder="-123456789"></div>
      <div class="form-group"><label>Интервал (сек)</label><input type="number" id="autopost-interval" value="120"></div>
      <div class="form-group"><label>Сообщение</label><textarea id="autopost-message" rows="2"></textarea></div>
    </div>
    <div class="flex mt-2"><button class="btn" onclick="saveAutoPostSettings()">💾 Сохранить</button><button class="btn btn-secondary" onclick="sendTestPost()">📤 Тест</button></div>
  </div>
</div>

<!-- ====== ДОВЕРЕННЫЕ ====== -->
<div id="trusted" class="tab-content hidden">
  <div class="card">
    <div class="card-title">🔒 Доверенные пользователи</div>
    <div class="form-group"><label>Добавить по ID или ссылке VK</label><div class="flex"><input type="text" id="trusted-input" placeholder="vk.com/id123456 или 123456" style="flex:1"><button class="btn" onclick="addTrusted()">➕</button></div></div>
    <div class="table-wrap"><table><thead><tr><th>ID</th><th>Имя</th><th>Статус</th><th></th></tr></thead><tbody id="trusted-list"></tbody></table></div>
  </div>
</div>

<!-- ====== НАСТРОЙКИ ====== -->
<div id="settings" class="tab-content hidden">
  <div class="grid-2">
    <div class="card">
      <div class="card-title">⚙️ Основные</div>
      <div class="form-group"><label>Префикс</label><input type="text" id="cfg-prefix" value="!"></div>
      <div class="form-group"><label>Интервал статуса (сек)</label><input type="number" id="cfg-status-interval" value="30"></div>
      <div class="form-group"><label>Интервал автолайка (сек)</label><input type="number" id="cfg-like-interval" value="30"></div>
      <button class="btn" onclick="saveBasicSettings()">💾 Сохранить</button>
    </div>
    <div class="card">
      <div class="card-title">🔑 Токен бота</div>
      <div class="form-group"><label>Токен</label><input type="password" id="cfg-token" readonly value="************"></div>
      <div class="flex mt-2"><button class="btn btn-secondary" onclick="showToken()">👁️ Показать</button><button class="btn btn-secondary" onclick="copyToken()">📋 Копировать</button></div>
    </div>
  </div>
</div>

<!-- ====== ЧС ====== -->
<div id="blacklist" class="tab-content hidden">
  <div class="card">
    <div class="card-title">🚫 Черный список</div>
    <div class="form-group"><label>Добавить в ЧС (ID или ссылка)</label><div class="flex"><input type="text" id="bl-input" placeholder="id123456" style="flex:1"><button class="btn btn-danger" onclick="addToBlacklist()">🚫</button></div></div>
    <div class="table-wrap"><table><thead><tr><th>ID</th><th>Имя</th><th></th></tr></thead><tbody id="bl-list"></tbody></table></div>
  </div>
</div>

<!-- ====== АВТОПОСТ ====== -->
<div id="autopost" class="tab-content hidden">
  <div class="card">
    <div class="card-title">📢 Автопостинг</div>
    <div class="grid-2">
      <div class="form-group"><label>Статус</label><button id="ap-status-btn" class="btn btn-secondary" onclick="toggleAutoPost()">Включить</button></div>
      <div class="form-group"><label>ID группы</label><input type="text" id="ap-group" placeholder="-123456789"></div>
      <div class="form-group"><label>Интервал (сек)</label><input type="number" id="ap-interval" value="120"></div>
      <div class="form-group"><label>Сообщение</label><textarea id="ap-message" rows="2"></textarea></div>
    </div>
    <div class="flex mt-2"><button class="btn" onclick="saveAutoPostSettings()">💾 Сохранить</button><button class="btn btn-secondary" onclick="sendTestPost()">📤 Тест</button></div>
  </div>
</div>

<!-- ====== UPLP ====== -->
<div id="uplp" class="tab-content hidden">
  <div class="card">
    <div class="card-title">📈 UPLP (Автопродвижение)</div>
    <div class="grid-2">
      <div class="form-group"><label>Статус</label><button id="uplp-status-btn" class="btn btn-secondary" onclick="toggleUPLP()">Включить</button></div>
      <div class="form-group"><label>ID группы</label><input type="text" id="uplp-group" placeholder="-123456789"></div>
      <div class="form-group"><label>Время публикации (ЧЧ:ММ)</label><input type="text" id="uplp-time" placeholder="12:00"></div>
      <div class="form-group"><label>Ссылка для покупки</label><input type="text" id="uplp-link" placeholder="vk.com/..."></div>
      <div class="form-group"><label>Цена</label><input type="text" id="uplp-price" placeholder="100р навсегда"></div>
      <div class="form-group"><label>Поддержка</label><input type="text" id="uplp-support" placeholder="месяц"></div>
    </div>
    <div class="flex mt-2"><button class="btn" onclick="saveUPLPSettings()">💾 Сохранить</button><button class="btn btn-secondary" onclick="resetUPLP()">🔄 Сбросить историю</button></div>
  </div>
</div>

<!-- ====== РЕДАКТОР ====== -->
<div id="editor" class="tab-content hidden">
  <div class="card">
    <div class="card-title">📝 Редактор модулей</div>
    <div class="card-subtitle">Редактируй .py файлы бота прямо здесь. Будь осторожен!</div>
    <div class="grid-2">
      <div>
        <div class="form-group"><label>Файлы</label><div class="file-list" id="editor-files"></div></div>
      </div>
      <div>
        <div class="form-group"><label>Код (<span id="editor-filename">выберите файл</span>)</label><textarea class="editor-area" id="editor-code" placeholder="Выберите файл слева..."></textarea></div>
        <div class="flex"><button class="btn" onclick="saveEditorFile()">💾 Сохранить файл</button><button class="btn btn-secondary" onclick="loadEditorFiles()">🔄 Обновить список</button></div>
      </div>
    </div>
  </div>
</div>

<!-- ====== КОНСТРУКТОР ====== -->
<div id="constructor" class="tab-content hidden">
  <div class="card">
    <div class="card-title">🚀 Конструктор модулей</div>
    <div class="card-subtitle">Создай свой Python-модуль без перезапуска</div>
    <div class="form-group"><label>Название модуля (латиница)</label><input type="text" id="mod-name" placeholder="mymodule"></div>
    <div class="form-group"><label>Команды (каждая строка: команда=ответ)</label><textarea id="mod-simple" rows="5" placeholder="привет=Привет, мир!\nпока=До свидания!"></textarea></div>
    <button class="btn" onclick="createModule()">🚀 Создать модуль</button>
  </div>
  <div class="card">
    <div class="card-title">📦 Созданные модули</div>
    <div class="table-wrap"><table><thead><tr><th>Файл</th><th>Команды</th><th></th></tr></thead><tbody id="modules-list"></tbody></table></div>
  </div>
</div>

</div>

<!-- НИЖНЯЯ НАВИГАЦИЯ -->
<div class="bottom-nav">
  <button class="nav-btn" onclick="showToast('Меню')">☰</button>
  <button class="nav-btn active" onclick="switchTab('dashboard');document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));event.target.classList.add('active')">○</button>
  <button class="nav-btn" onclick="history.back()">△</button>
</div>

<script>
let currentTab='dashboard';

function switchTab(tab){
  document.querySelectorAll('.tab-content').forEach(e=>e.classList.add('hidden'));
  document.getElementById(tab).classList.remove('hidden');
  document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));
  event.target.classList.add('active');
  currentTab=tab;
  loadTabData(tab);
}

function loadTabData(tab){
  if(tab==='dashboard')loadDashboard();
  else if(tab==='commands')loadCommands();
  else if(tab==='trusted')loadTrusted();
  else if(tab==='blacklist')loadBlacklist();
  else if(tab==='modules')loadModules();
  else if(tab==='autopost')loadAutoPost();
  else if(tab==='uplp')loadUPLP();
  else if(tab==='editor')loadEditorFiles();
  else if(tab==='constructor')loadConstructor();
}

/* ===== DASHBOARD ===== */
function loadDashboard(){
  fetch('/api/status').then(r=>r.json()).then(d=>{
    document.getElementById('uptime').innerText=d.uptime||'--';
    document.getElementById('total-commands').innerText=d.total_commands||0;
    document.getElementById('trusted-count').innerText=d.trusted_count||0;
    document.getElementById('custom-count').innerText=d.custom_commands_count||0;
    document.getElementById('rp-count').innerText=d.rp_count||0;
    document.getElementById('anim-count').innerText=d.anim_count||0;
  });
  fetch('/api/animations').then(r=>r.json()).then(d=>{
    if(d.current)document.getElementById('animation-select').value=d.current;
    const b=document.getElementById('toggle-status-btn');
    b.innerText=d.auto_enabled?'Выключить':'Включить';
    b.className=d.auto_enabled?'btn btn-danger':'btn btn-secondary';
  });
}

/* ===== COMMANDS ===== */
function loadCommands(){
  fetch('/api/commands/list').then(r=>r.json()).then(d=>{
    const tb=document.getElementById('commands-list');
    if(d.commands&&Object.keys(d.commands).length){
      tb.innerHTML=Object.entries(d.commands).map(([n,i])=>`<tr><td><code style="background:rgba(255,107,107,0.15);color:#ff6b6b;padding:2px 8px;border-radius:6px;">!${n}</code></td><td>${i.description||'—'}</td><td><button class="btn btn-danger btn-sm" onclick="deleteCommand('${n}')">🗑️</button></td></tr>`).join('');
    }else tb.innerHTML='<tr><td colspan="3" style="text-align:center;color:#666">Нет команд</td></tr>';
  });
}
function createCommand(){
  const n=document.getElementById('cmd-name').value.trim();
  const desc=document.getElementById('cmd-desc').value.trim();
  const resp=document.getElementById('cmd-response').value.trim();
  if(!n||!resp){showToast('Заполните название и ответ','error');return;}
  fetch('/api/commands/create',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n,description:desc,response:resp})})
    .then(r=>r.json()).then(d=>{if(d.success){showToast('Команда создана!');document.getElementById('cmd-name').value='';document.getElementById('cmd-desc').value='';document.getElementById('cmd-response').value='';loadCommands();loadDashboard();}else showToast(d.error||'Ошибка','error');});
}
function deleteCommand(n){if(!confirm(`Удалить !${n}?`))return;fetch('/api/commands/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n})}).then(r=>r.json()).then(d=>{if(d.success){showToast('Удалена');loadCommands();loadDashboard();}});}

/* ===== MODULES ===== */
function loadModules(){
  fetch('/api/rp/list').then(r=>r.json()).then(d=>{
    const tb=document.getElementById('rp-list');
    if(d.commands)tb.innerHTML=Object.entries(d.commands).map(([n,i])=>`<tr><td>${n}</td><td>${i.emoji}</td><td>${i.text}</td><td><button class="btn btn-danger btn-sm" onclick="deleteRP('${n}')">🗑️</button></td></tr>`).join('');
  });
  fetch('/api/anime/settings').then(r=>r.json()).then(d=>{
    document.getElementById('nsfw-mode').value=d.nsfw_mode?'true':'false';
    document.getElementById('sfw-groups').value=(d.sfw_groups||[]).join(', ');
    document.getElementById('nsfw-groups').value=(d.nsfw_groups||[]).join(', ');
  });
  fetch('/api/autopost/status').then(r=>r.json()).then(d=>{
    const b=document.getElementById('autopost-toggle-btn');
    b.innerText=d.enabled?'Выключить':'Включить';b.className=d.enabled?'btn btn-danger':'btn btn-secondary';
    if(d.group_id)document.getElementById('autopost-group').value=d.group_id;
    if(d.interval)document.getElementById('autopost-interval').value=d.interval;
    if(d.message)document.getElementById('autopost-message').value=d.message;
  });
}
function addRPCommand(){
  const n=document.getElementById('rp-name').value.trim();
  const t=document.getElementById('rp-text').value.trim();
  const e=document.getElementById('rp-emoji').value.trim()||'🎭';
  if(!n||!t){showToast('Заполните название и текст','error');return;}
  fetch('/api/rp/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n,text:t,emoji:e})})
    .then(r=>r.json()).then(d=>{if(d.success){showToast('RP добавлена');document.getElementById('rp-name').value='';document.getElementById('rp-text').value='';document.getElementById('rp-emoji').value='';loadModules();}else showToast(d.error,'error');});
}
function deleteRP(n){if(!confirm(`Удалить RP ${n}?`))return;fetch('/api/rp/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n})}).then(r=>r.json()).then(d=>{if(d.success){showToast('Удалена');loadModules();}});}
function saveAnimeSettings(){
  const data={nsfw_mode:document.getElementById('nsfw-mode').value==='true',sfw_groups:document.getElementById('sfw-groups').value.split(',').map(s=>parseInt(s.trim())).filter(n=>!isNaN(n)),nsfw_groups:document.getElementById('nsfw-groups').value.split(',').map(s=>parseInt(s.trim())).filter(n=>!isNaN(n))};
  fetch('/api/anime/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}).then(r=>r.json()).then(d=>{if(d.success)showToast('Anime сохранено');});
}
function toggleAutoPost(){
  fetch('/api/autopost/toggle',{method:'POST'}).then(r=>r.json()).then(d=>{showToast(d.enabled?'Автопост включен':'Автопост выключен');loadModules();loadAutoPost();});
}
function saveAutoPostSettings(){
  const g=parseInt(document.getElementById('autopost-group').value)||parseInt(document.getElementById('ap-group').value);
  const i=parseInt(document.getElementById('autopost-interval').value)||parseInt(document.getElementById('ap-interval').value);
  const m=document.getElementById('autopost-message').value||document.getElementById('ap-message').value;
  fetch('/api/autopost/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({group_id:g,interval:i,message:m})}).then(r=>r.json()).then(d=>{if(d.success)showToast('Автопост сохранен');});
}
function sendTestPost(){
  fetch('/api/autopost/test',{method:'POST'}).then(r=>r.json()).then(d=>showToast(d.success?'Тест отправлен!':'Ошибка: '+(d.error||'?'),d.success?'success':'error'));
}

/* ===== TRUSTED ===== */
function loadTrusted(){
  fetch('/api/trusted/list').then(r=>r.json()).then(d=>{
    const tb=document.getElementById('trusted-list');
    if(d.users&&d.users.length){
      tb.innerHTML=d.users.map(u=>`<tr><td><a href="https://vk.com/id${u.id}" target="_blank" style="color:#60a5fa">${u.id}</a></td><td>${u.name||'Неизвестно'}</td><td>${u.is_owner?'<span class="badge badge-blue">👑 Владелец</span>':'<<span class="badge badge-green">Доверенный</span>'}</td><td>${u.is_owner?'':`<button class="btn btn-danger btn-sm" onclick="removeTrusted(${u.id})">🗑️</button>`}</td></tr>`).join('');
    }else tb.innerHTML='<tr><td colspan="4" style="text-align:center;color:#666">Нет доверенных</td></tr>';
  });
}
function addTrusted(){
  const v=document.getElementById('trusted-input').value.trim();
  if(!v)return;
  fetch('/api/trusted/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:v})}).then(r=>r.json()).then(d=>{if(d.success){showToast('Добавлено');document.getElementById('trusted-input').value='';loadTrusted();loadDashboard();}else showToast(d.error,'error');});
}
function removeTrusted(id){if(!confirm('Удалить из доверенных?'))return;fetch('/api/trusted/remove',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id})}).then(r=>r.json()).then(d=>{if(d.success){showToast('Удалено');loadTrusted();loadDashboard();}});}

/* ===== BLACKLIST ===== */
function loadBlacklist(){
  fetch('/api/blacklist/list').then(r=>r.json()).then(d=>{
    const tb=document.getElementById('bl-list');
    if(d.users&&d.users.length){
      tb.innerHTML=d.users.map(u=>`<tr><td>${u.id}</td><td>${u.name||'Неизвестно'}</td><td><button class="btn btn-danger btn-sm" onclick="removeFromBL(${u.id})">🗑️ Разблокировать</button></td></tr>`).join('');
    }else tb.innerHTML='<tr><td colspan="3" style="text-align:center;color:#666">ЧС пуст</td></tr>';
  });
}
function addToBlacklist(){
  const v=document.getElementById('bl-input').value.trim();
  if(!v)return;
  fetch('/api/blacklist/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:v})}).then(r=>r.json()).then(d=>{if(d.success){showToast('Добавлено в ЧС');document.getElementById('bl-input').value='';loadBlacklist();}else showToast(d.error,'error');});
}
function removeFromBL(id){if(!confirm('Разблокировать?'))return;fetch('/api/blacklist/remove',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id})}).then(r=>r.json()).then(d=>{if(d.success){showToast('Разблокировано');loadBlacklist();}});}

/* ===== SETTINGS ===== */
function saveBasicSettings(){
  const data={prefix:document.getElementById('cfg-prefix').value,status_interval:parseInt(document.getElementById('cfg-status-interval').value),like_interval:parseInt(document.getElementById('cfg-like-interval').value)};
  fetch('/api/settings/basic',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}).then(r=>r.json()).then(d=>{if(d.success)showToast('Настройки сохранены');});
}
function showToken(){
  fetch('/api/token/get').then(r=>r.json()).then(d=>{
    const i=document.getElementById('cfg-token');i.type='text';i.value=d.token;setTimeout(()=>{i.type='password';i.value='************';},5000);
  });
}
function copyToken(){
  fetch('/api/token/get').then(r=>r.json()).then(d=>navigator.clipboard.writeText(d.token).then(()=>showToast('Токен скопирован!')));
}

/* ===== UPLP ===== */
function loadUPLP(){
  fetch('/api/uplp/status').then(r=>r.json()).then(d=>{
    const b=document.getElementById('uplp-status-btn');
    b.innerText=d.enabled?'Выключить':'Включить';b.className=d.enabled?'btn btn-danger':'btn btn-secondary';
    if(d.group_id)document.getElementById('uplp-group').value=d.group_id;
    if(d.post_time)document.getElementById('uplp-time').value=d.post_time;
    if(d.promote_link)document.getElementById('uplp-link').value=d.promote_link;
    if(d.price)document.getElementById('uplp-price').value=d.price;
    if(d.support_period)document.getElementById('uplp-support').value=d.support_period;
  });
}
function toggleUPLP(){
  fetch('/api/uplp/toggle',{method:'POST'}).then(r=>r.json()).then(d=>{showToast(d.enabled?'UPLP включен':'UPLP выключен');loadUPLP();});
}
function saveUPLPSettings(){
  const data={group_id:parseInt(document.getElementById('uplp-group').value),post_time:document.getElementById('uplp-time').value,promote_link:document.getElementById('uplp-link').value,price:document.getElementById('uplp-price').value,support_period:document.getElementById('uplp-support').value};
  fetch('/api/uplp/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}).then(r=>r.json()).then(d=>{if(d.success)showToast('UPLP сохранено');});
}
function resetUPLP(){if(!confirm('Сбросить историю публикаций?'))return;fetch('/api/uplp/reset',{method:'POST'}).then(r=>r.json()).then(d=>{if(d.success)showToast('История сброшена');});}

/* ===== EDITOR ===== */
let currentEditFile='';
function loadEditorFiles(){
  fetch('/api/editor/files').then(r=>r.json()).then(d=>{
    const box=document.getElementById('editor-files');
    if(d.files&&d.files.length){
      box.innerHTML=d.files.map(f=>`<div class="file-item ${f===currentEditFile?'active':''}" onclick="loadFileCode('${f}')"><span>${f}</span><span>📝</span></div>`).join('');
    }else box.innerHTML='<div style="color:#666;font-size:13px">Нет файлов</div>';
  });
}
function loadFileCode(fn){
  currentEditFile=fn;
  document.getElementById('editor-filename').innerText=fn;
  fetch('/api/editor/file/'+encodeURIComponent(fn)).then(r=>r.json()).then(d=>{
    document.getElementById('editor-code').value=d.content||'';
    loadEditorFiles();
  });
}
function saveEditorFile(){
  if(!currentEditFile){showToast('Выберите файл','error');return;}
  if(!confirm('Сохранить изменения в '+currentEditFile+'?'))return;
  const code=document.getElementById('editor-code').value;
  fetch('/api/editor/file/'+encodeURIComponent(currentEditFile),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({content:code})})
    .then(r=>r.json()).then(d=>{if(d.success)showToast('Файл сохранен!');else showToast(d.error||'Ошибка','error');});
}

/* ===== CONSTRUCTOR ===== */
function loadConstructor(){
  fetch('/api/modules/list').then(r=>r.json()).then(d=>{
    const tb=document.getElementById('modules-list');
    if(d.modules&&d.modules.length){
      tb.innerHTML=d.modules.map(m=>`<tr><td><code style="color:#fbbf24">${m.name}</code></td><td>${m.commands_count}</td><td><button class="btn btn-danger btn-sm" onclick="deleteModule('${m.name}')">🗑️</button></td></tr>`).join('');
    }else tb.innerHTML='<tr><td colspan="3" style="text-align:center;color:#666">Нет модулей</td></tr>';
  });
}
function createModule(){
  const n=document.getElementById('mod-name').value.trim().toLowerCase();
  const simple=document.getElementById('mod-simple').value.trim();
  if(!n||!simple){showToast('Заполните название и команды','error');return;}
  if(!/^[a-z0-9_]+$/.test(n)){showToast('Только a-z, 0-9, _','error');return;}
  const commands={};
  simple.split('\\n').forEach(line=>{const p=line.split('=');if(p.length>=2)commands[p[0].trim()]=p.slice(1).join('=').trim();});
  if(!Object.keys(commands).length){showToast('Нет команд','error');return;}
  fetch('/api/modules/create',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n,commands})})
    .then(r=>r.json()).then(d=>{if(d.success){showToast('Модуль создан!');document.getElementById('mod-name').value='';document.getElementById('mod-simple').value='';loadConstructor();}else showToast(d.error||'Ошибка','error');});
}
function deleteModule(n){if(!confirm(`Удалить ${n}?`))return;fetch('/api/modules/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n})}).then(r=>r.json()).then(d=>{if(d.success){showToast('Модуль удален');loadConstructor();}});}

/* ===== UTILS ===== */
function changeAnimation(){
  const a=document.getElementById('animation-select').value;
  fetch('/api/animations/set',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({animation:a})}).then(r=>r.json()).then(d=>{if(d.success)showToast('Анимация изменена');});
}
function toggleAutoStatus(){
  fetch('/api/autostatus/toggle',{method:'POST'}).then(r=>r.json()).then(d=>{
    const b=document.getElementById('toggle-status-btn');
    b.innerText=d.enabled?'Выключить':'Включить';b.className=d.enabled?'btn btn-danger':'btn btn-secondary';
    showToast(d.enabled?'Автостатус включен':'Автостатус выключен');
  });
}
function showToast(msg,type='success'){
  const t=document.createElement('div');t.className=`toast toast-${type}`;t.innerText=msg;document.body.appendChild(t);setTimeout(()=>t.remove(),3000);
}
setInterval(()=>{if(currentTab==='dashboard')loadDashboard();},30000);
loadDashboard();
</script>
</body>
</html>
'''


class WebAdminModule:
    def __init__(self, bot: 'VKBot'):
        self.bot = bot
        self.app = Flask(__name__)
        self.server_thread = None
        self.is_running = False
        self.port = 5000
        self.host = '127.0.0.1'
        self.server = None
        self._setup_routes()

    def _setup_routes(self):
        # === HTML ===
        @self.app.route('/')
        def index():
            url = f"vk.com/id{self.bot.user_id}" if self.bot.user_id else "vk.com"
            return render_template_string(HTML_TEMPLATE, bot_url=url, start_date=datetime.now().strftime("%m/%d/%Y"))

        # === STATUS ===
        @self.app.route('/api/status')
        def api_status():
            from config import STATUS_ANIMATIONS, RP_COMMANDS
            uptime_str = "Только что"
            if hasattr(self.bot, 'start_time') and self.bot.start_time:
                uptime = time.time() - self.bot.start_time
                hours = int(uptime // 3600)
                minutes = int((uptime % 3600) // 60)
                uptime_str = f"{hours}ч {minutes}м"
            return jsonify({
                'uptime': uptime_str,
                'total_commands': len(self.bot.commands),
                'trusted_count': len(self.bot.trusted_users),
                'custom_commands_count': len(self.bot.custom_commands_module.custom_commands),
                'rp_count': len(RP_COMMANDS),
                'anim_count': len(STATUS_ANIMATIONS)
            })

        # === ANIMATIONS ===
        @self.app.route('/api/animations')
        def api_animations():
            return jsonify({
                'current': self.bot.animation_module.current_animation,
                'auto_enabled': self.bot.animation_module.auto_status_enabled
            })

        @self.app.route('/api/animations/set', methods=['POST'])
        def api_animations_set():
            data = request.json
            anim = data.get('animation')
            from config import STATUS_ANIMATIONS
            if anim in STATUS_ANIMATIONS:
                self.bot.animation_module.current_animation = anim
                return jsonify({'success': True})
            return jsonify({'success': False, 'error': 'Нет такой анимации'})

        @self.app.route('/api/autostatus/toggle', methods=['POST'])
        def api_autostatus_toggle():
            mod = self.bot.animation_module
            if mod.auto_status_enabled:
                mod.auto_status_enabled = False
                mod.status_animation_running = False
                try:
                    self.bot.vk.status.set(text="")
                except:
                    pass
            else:
                mod.auto_status_enabled = True
                mod.status_animation_running = True
                t = threading.Thread(target=mod.status_animation_loop, daemon=True)
                t.start()
            return jsonify({'enabled': mod.auto_status_enabled})

        # === COMMANDS ===
        @self.app.route('/api/commands/list')
        def api_commands_list():
            return jsonify({'commands': self.bot.custom_commands_module.custom_commands})

        @self.app.route('/api/commands/create', methods=['POST'])
        def api_commands_create():
            data = request.json
            name = data.get('name', '').lower().strip()
            desc = data.get('description', '')
            response = data.get('response', '')
            if not name or not response:
                return jsonify({'success': False, 'error': 'Заполните название и ответ'})
            if name in self.bot.commands or name in self.bot.custom_commands_module.custom_commands:
                return jsonify({'success': False, 'error': 'Команда уже существует'})
            if not re.match(r'^[a-zа-яё0-9_]+$', name):
                return jsonify({'success': False, 'error': 'Недопустимые символы'})
            self.bot.custom_commands_module.custom_commands[name] = {
                'description': desc,
                'response': response,
                'created_by': self.bot.user_id,
                'created_at': datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            }
            self.bot.custom_commands_module.save_custom_commands()
            self.bot.custom_commands_module.register_custom_command(name)
            log(f"Создана команда через админку: {name}", "SUCCESS")
            return jsonify({'success': True})

        @self.app.route('/api/commands/delete', methods=['POST'])
        def api_commands_delete():
            data = request.json
            name = data.get('name', '').lower()
            if name in self.bot.custom_commands_module.custom_commands:
                del self.bot.custom_commands_module.custom_commands[name]
                if name in self.bot.commands:
                    del self.bot.commands[name]
                self.bot.custom_commands_module.save_custom_commands()
                log(f"Удалена команда через админку: {name}", "WARNING")
            return jsonify({'success': True})

        # === RP ===
        @self.app.route('/api/rp/list')
        def api_rp_list():
            from config import RP_COMMANDS
            return jsonify({'commands': RP_COMMANDS})

        @self.app.route('/api/rp/add', methods=['POST'])
        def api_rp_add():
            data = request.json
            name = data.get('name', '').lower().strip()
            text = data.get('text', '')
            emoji = data.get('emoji', '🎭')
            if not name or not text:
                return jsonify({'success': False, 'error': 'Заполните название и текст'})
            from config import RP_COMMANDS
            RP_COMMANDS[name] = {'emoji': emoji, 'text': text, 'declension': name}
            self._save_rp_to_config()
            self.bot.rp_module.register_commands()
            log(f"Добавлена RP через админку: {name}", "SUCCESS")
            return jsonify({'success': True})

        @self.app.route('/api/rp/delete', methods=['POST'])
        def api_rp_delete():
            data = request.json
            name = data.get('name', '').lower()
            from config import RP_COMMANDS
            if name in RP_COMMANDS:
                del RP_COMMANDS[name]
                self._save_rp_to_config()
                if name in self.bot.commands:
                    del self.bot.commands[name]
                log(f"Удалена RP через админку: {name}", "WARNING")
            return jsonify({'success': True})

        # === ANIME ===
        @self.app.route('/api/anime/settings')
        def api_anime_settings():
            try:
                from anime import anime_api
                return jsonify({
                    'nsfw_mode': anime_api.nsfw_mode,
                    'sfw_groups': anime_api.sfw_groups,
                    'nsfw_groups': anime_api.nsfw_groups
                })
            except:
                return jsonify({'nsfw_mode': False, 'sfw_groups': [], 'nsfw_groups': []})

        @self.app.route('/api/anime/save', methods=['POST'])
        def api_anime_save():
            data = request.json
            try:
                from anime import anime_api
                anime_api.nsfw_mode = data.get('nsfw_mode', False)
                anime_api.sfw_groups = data.get('sfw_groups', [])
                anime_api.nsfw_groups = data.get('nsfw_groups', [])
                log("Anime настройки сохранены", "SUCCESS")
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

        # === AUTOPOST ===
        @self.app.route('/api/autopost/status')
        def api_autopost_status():
            mod = self.bot.auto_poster_module
            return jsonify({
                'enabled': mod.auto_post_enabled,
                'group_id': mod.group_id,
                'interval': mod.interval,
                'message': mod.message
            })

        @self.app.route('/api/autopost/toggle', methods=['POST'])
        def api_autopost_toggle():
            mod = self.bot.auto_poster_module
            if mod.auto_post_enabled:
                mod.auto_post_enabled = False
                log("Автопост выключен", "WARNING")
            else:
                mod.auto_post_enabled = True
                t = threading.Thread(target=mod.auto_post_loop, daemon=True)
                t.start()
                log("Автопост включен", "SUCCESS")
            return jsonify({'enabled': mod.auto_post_enabled})

        @self.app.route('/api/autopost/save', methods=['POST'])
        def api_autopost_save():
            data = request.json
            mod = self.bot.auto_poster_module
            if 'group_id' in data:
                mod.group_id = data['group_id']
            if 'interval' in data:
                mod.interval = max(5, data['interval'])
            if 'message' in data:
                mod.message = data['message'][:500]
            log("Автопост настройки сохранены", "SUCCESS")
            return jsonify({'success': True})

        @self.app.route('/api/autopost/test', methods=['POST'])
        def api_autopost_test():
            mod = self.bot.auto_poster_module
            success, error = mod.send_post(mod.message)
            return jsonify({'success': success, 'error': error})

        # === UPLP ===
        @self.app.route('/api/uplp/status')
        def api_uplp_status():
            mod = self.bot.uplp_module
            return jsonify({
                'enabled': mod.enabled,
                'group_id': mod.group_id,
                'post_time': mod.post_time,
                'promote_link': mod.promote_link,
                'price': mod.price,
                'support_period': mod.support_period
            })

        @self.app.route('/api/uplp/toggle', methods=['POST'])
        def api_uplp_toggle():
            mod = self.bot.uplp_module
            if mod.enabled:
                mod.enabled = False
                log("UPLP выключен", "WARNING")
            else:
                mod.enabled = True
                t = threading.Thread(target=mod.promote_loop, daemon=True)
                t.start()
                log("UPLP включен", "SUCCESS")
            mod.save_state()
            return jsonify({'enabled': mod.enabled})

        @self.app.route('/api/uplp/save', methods=['POST'])
        def api_uplp_save():
            data = request.json
            mod = self.bot.uplp_module
            if 'group_id' in data:
                mod.group_id = data['group_id']
            if 'post_time' in data:
                mod.post_time = data['post_time']
            if 'promote_link' in data:
                mod.promote_link = data['promote_link']
            if 'price' in data:
                mod.price = data['price']
            if 'support_period' in data:
                mod.support_period = data['support_period']
            mod.save_state()
            log("UPLP настройки сохранены", "SUCCESS")
            return jsonify({'success': True})

        @self.app.route('/api/uplp/reset', methods=['POST'])
        def api_uplp_reset():
            mod = self.bot.uplp_module
            mod.posted_indices = []
            mod.save_state()
            log("UPLP сброшен", "WARNING")
            return jsonify({'success': True})

        # === TRUSTED ===
        @self.app.route('/api/trusted/list')
        def api_trusted_list():
            users = []
            for uid in self.bot.trusted_users:
                try:
                    user = self.bot.vk.users.get(user_ids=uid)[0]
                    name = f"{user['first_name']} {user['last_name']}"
                except:
                    name = "Неизвестно"
                users.append({'id': uid, 'name': name, 'is_owner': uid == self.bot.user_id})
            return jsonify({'users': users})

        @self.app.route('/api/trusted/add', methods=['POST'])
        def api_trusted_add():
            data = request.json
            user_input = str(data.get('id', ''))
            user_id = self.bot.parse_user_id(user_input)
            if not user_id:
                return jsonify({'success': False, 'error': 'Не удалось определить ID'})
            if user_id == self.bot.user_id:
                return jsonify({'success': False, 'error': 'Владелец уже в доверенных'})
            self.bot.trusted_users.add(user_id)
            self.bot.save_trusted_users()
            log(f"Добавлен доверенный: {user_id}", "SUCCESS")
            return jsonify({'success': True})

        @self.app.route('/api/trusted/remove', methods=['POST'])
        def api_trusted_remove():
            data = request.json
            user_id = data.get('id')
            if user_id == self.bot.user_id:
                return jsonify({'success': False, 'error': 'Нельзя удалить владельца'})
            self.bot.trusted_users.discard(user_id)
            self.bot.save_trusted_users()
            log(f"Удален доверенный: {user_id}", "WARNING")
            return jsonify({'success': True})

        # === BLACKLIST ===
        @self.app.route('/api/blacklist/list')
        def api_blacklist_list():
            users = []
            bl_file = "blacklist.json"
            if os.path.exists(bl_file):
                try:
                    with open(bl_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for uid in data.get('blacklist', []):
                            try:
                                user = self.bot.vk.users.get(user_ids=uid)[0]
                                name = f"{user['first_name']} {user['last_name']}"
                            except:
                                name = "Неизвестно"
                            users.append({'id': uid, 'name': name})
                except:
                    pass
            return jsonify({'users': users})

        @self.app.route('/api/blacklist/add', methods=['POST'])
        def api_blacklist_add():
            data = request.json
            user_input = str(data.get('id', ''))
            user_id = self.bot.parse_user_id(user_input)
            if not user_id:
                return jsonify({'success': False, 'error': 'Не удалось определить ID'})
            try:
                self.bot.vk.account.banUser(owner_id=user_id)
                bl_file = "blacklist.json"
                bl_data = {"blacklist": []}
                if os.path.exists(bl_file):
                    with open(bl_file, 'r', encoding='utf-8') as f:
                        bl_data = json.load(f)
                if user_id not in bl_data["blacklist"]:
                    bl_data["blacklist"].append(user_id)
                with open(bl_file, 'w', encoding='utf-8') as f:
                    json.dump(bl_data, f, ensure_ascii=False, indent=2)
                log(f"Добавлен в ЧС: {user_id}", "SUCCESS")
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

        @self.app.route('/api/blacklist/remove', methods=['POST'])
        def api_blacklist_remove():
            data = request.json
            user_id = data.get('id')
            try:
                self.bot.vk.account.unbanUser(owner_id=user_id)
            except:
                pass
            bl_file = "blacklist.json"
            if os.path.exists(bl_file):
                try:
                    with open(bl_file, 'r', encoding='utf-8') as f:
                        bl_data = json.load(f)
                    if user_id in bl_data.get("blacklist", []):
                        bl_data["blacklist"].remove(user_id)
                    with open(bl_file, 'w', encoding='utf-8') as f:
                        json.dump(bl_data, f, ensure_ascii=False, indent=2)
                except:
                    pass
            log(f"Удален из ЧС: {user_id}", "WARNING")
            return jsonify({'success': True})

        # === SETTINGS ===
        @self.app.route('/api/settings/basic', methods=['POST'])
        def api_settings_basic():
            data = request.json
            from config import CONFIG
            if 'prefix' in data and data['prefix']:
                CONFIG['COMMAND_PREFIX'] = data['prefix']
            if 'status_interval' in data:
                CONFIG['STATUS_UPDATE_INTERVAL'] = data['status_interval']
            if 'like_interval' in data:
                CONFIG['AUTO_LIKE_CHECK_INTERVAL'] = data['like_interval']
            log("Базовые настройки сохранены", "SUCCESS")
            return jsonify({'success': True})

        @self.app.route('/api/token/get')
        def api_token_get():
            from config import CONFIG
            return jsonify({'token': CONFIG.get('TOKEN', '')})

        # === EDITOR ===
        @self.app.route('/api/editor/files')
        def api_editor_files():
            files = [f for f in os.listdir('.') if f.endswith('.py') and f != 'web_admin.py']
            files.sort()
            return jsonify({'files': files})

        @self.app.route('/api/editor/file/<filename>')
        def api_editor_file(filename):
            safe = os.path.basename(filename)
            path = os.path.join('.', safe)
            if not os.path.exists(path) or not safe.endswith('.py'):
                return jsonify({'success': False, 'error': 'Файл не найден'})
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return jsonify({'success': True, 'content': content})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

        @self.app.route('/api/editor/file/<filename>', methods=['POST'])
        def api_editor_save(filename):
            safe = os.path.basename(filename)
            path = os.path.join('.', safe)
            if not safe.endswith('.py'):
                return jsonify({'success': False, 'error': 'Только .py файлы'})
            data = request.json
            content = data.get('content', '')
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                log(f"Файл {safe} отредактирован через админку", "WARNING")
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

        # === MODULE CONSTRUCTOR ===
        @self.app.route('/api/modules/list')
        def api_modules_list():
            modules = []
            for f in os.listdir('.'):
                if f.endswith('_module.py'):
                    try:
                        with open(f, 'r', encoding='utf-8') as file:
                            content = file.read()
                        count = content.count('self.bot.commands[')
                        modules.append({'name': f, 'commands_count': count})
                    except:
                        modules.append({'name': f, 'commands_count': 0})
            return jsonify({'modules': modules})

        @self.app.route('/api/modules/create', methods=['POST'])
        def api_modules_create():
            data = request.json
            name = data.get('name', '').lower().strip()
            commands = data.get('commands', {})
            if not name or not commands:
                return jsonify({'success': False, 'error': 'Заполните название и команды'})
            if not all(c.isalnum() or c == '_' for c in name):
                return jsonify({'success': False, 'error': 'Недопустимые символы'})
            filename = f"{name}_module.py"
            if os.path.exists(filename):
                return jsonify({'success': False, 'error': 'Модуль уже существует'})

            cmd_lines = []
            for cmd_name, response in commands.items():
                safe = response.replace('"', '\\"').replace("'", "\\'")
                cmd_lines.append(f'        self.bot.commands["{cmd_name}"] = lambda e, a: self.bot.send_message(e.peer_id, "{safe}")')

            module_code = f'''"""
Автоматически созданный модуль: {name}
Создан: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}
"""
from typing import TYPE_CHECKING
from utils import log

if TYPE_CHECKING:
    from bot import VKBot

class {name.capitalize()}Module:
    def __init__(self, bot: 'VKBot'):
        self.bot = bot

    def register_commands(self):
{chr(10).join(cmd_lines)}
        log(f"Модуль {name} загружен", "SUCCESS")

    def stop(self):
        log("Модуль {name} остановлен", "WARNING")

def create_module(bot):
    m = {name.capitalize()}Module(bot)
    m.register_commands()
    return m
'''
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(module_code)
            log(f"Создан модуль: {filename}", "SUCCESS")
            return jsonify({'success': True, 'file': filename})

        @self.app.route('/api/modules/delete', methods=['POST'])
        def api_modules_delete():
            data = request.json
            name = data.get('name', '').strip()
            if os.path.exists(name):
                try:
                    os.remove(name)
                    log(f"Удален модуль: {name}", "WARNING")
                    return jsonify({'success': True})
                except Exception as e:
                    return jsonify({'success': False, 'error': str(e)})
            return jsonify({'success': False, 'error': 'Файл не найден'})

    def _save_rp_to_config(self):
        from config import RP_COMMANDS
        try:
            with open('config.py', 'r', encoding='utf-8') as f:
                content = f.read()
            import re
            pattern = r'RP_COMMANDS\s*=\s*\{.*?\}(?=\n|$)'
            new_rp = "RP_COMMANDS = " + json.dumps(RP_COMMANDS, ensure_ascii=False, indent=4)
            new_rp = new_rp.replace('"', "'")
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, new_rp, content, flags=re.DOTALL)
                with open('config.py', 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                with open('config.py', 'a', encoding='utf-8') as f:
                    f.write("\n\n" + new_rp + "\n")
        except Exception as e:
            log(f"Ошибка сохранения RP: {e}", "ERROR")

    def register_commands(self):
        self.bot.commands["админ"] = self.cmd_admin
        self.bot.commands["admin"] = self.cmd_admin

    def cmd_admin(self, event, args):
        self.bot.send_message(event.peer_id,
            f"🔧 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟:\n\n🌐 http://{self.host}:{self.port}/\n💡 Для доступа с телефона используйте ngrok",
            reply_to=event.message_id if not event.from_me else None)

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        log(f"🌐 Админ-панель: http://{self.host}:{self.port}/", "SUCCESS")

    def _run_server(self):
        try:
            from werkzeug.serving import make_server
            self.server = make_server(self.host, self.port, self.app)
            self.server.serve_forever()
        except Exception as e:
            log(f"Ошибка веб-сервера: {e}", "ERROR")

    def stop(self):
        self.is_running = False
        if self.server:
            try:
                self.server.shutdown()
            except:
                pass
        log("Админ-панель остановлена", "WARNING")
