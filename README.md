# Harness Utils (`harness-utils`)

**Harness Utils** є інструментом для автоматизації створення харнесс-файлів (тестове середовище, лінтери, конфігурації, CI та інструкції для AI агентів) у Python проектах, а також для встановлення та управління Windows скриптами у системі.

---

## 🌟 Основні можливості

1. **Генератор harness файлів для Python проектів (`harness-create`)**:
   - Автоматичне створення `pyproject.toml` (з налаштуваннями `pytest`, `ruff`, `mypy`, `coverage`).
   - Конфігурації `.gitignore`, `.env.example`, `.pre-commit-config.yaml`.
   - Інструкції та стандарти розробки `AGENTS.md`, `PROGRESS.md`, `DECISIONS.md`.
   - CI pipeline у `.github/workflows/ci.yml`.
   - Базова структура коду `src/<package_name>/` та тестів `tests/`.

2. **Windows Інсталятор Скриптів (`harness-installer`)**:
   - Graphical Wizard GUI (на базі Tkinter) та CLI режими.
   - Динамічне сканування директорії `script/` для файлів `.ps1`, `.bat`, `.cmd`, `.vbs`, `.py`, `.sh`.
   - **Можливість додавання нових скриптів**: додавання нових скриптів через GUI ("➕ Add Custom Script...") або CLI (`--add-script path/to/script.ps1`).
   - Автоматичне створення обгорток командного рядка (`.bat` launchers) для запуска PowerShell та Python скриптів напряму з консолі.
   - Додавання директорії встановлення у системну/користувацьку змінну оточення `PATH` з сповіщенням Windows (`WM_SETTINGCHANGE`).
   - Створення ярликів на Робочому столі та у меню Пуск ("Start Menu").
   - Реєстрація деінсталятора у системі Windows (у списку "Програми та засоби" / "Add or remove programs").

3. **Збірка автономного Windows Інсталятора (`build-installer`)**:
   - Компіляція у повністю автономний `.exe` файл за допомогою `PyInstaller`.

---

## 🚀 Встановлення та Швидкий Старт

### Встановлення у режимі розробки
```bash
pip install -e ".[dev]"
```

---

## 🛠️ Використання

### 1. Створення Harness у новому або існуючому проекті

За допомогою консольної команди:
```bash
harness-create my_new_project --target C:/Projects/my_new_project
```
або через загальний CLI:
```bash
harness-utils create-harness my_new_project --target C:/Projects/my_new_project
```

### 2. Запуск Windows Інсталятора Скриптів

#### Графічний майстер (GUI)
Запустіть підключений скрипт у проекті:
- Double-click `scripts/install_scripts.bat` або запустіть у PowerShell `.\script\install_scripts.ps1`
- Або виконай в консолі:
  ```bash
  harness-installer --gui
  ```

#### Консольний режим (CLI)
Переглянути список доступних скриптів:
```bash
harness-installer --list
```

Встановити всі виявлені скрипти за замовчуванням у `%LocalAppData%\Programs\HarnessUtils`:
```bash
harness-installer
```

#### Додавання нового скрипта
Додати новий скрипт до інсталятора:
```bash
harness-installer --add-script C:/path/to/my_custom_script.ps1
```

### 3. Збірка Standalone `.exe` Інсталятора

Для створення готового до розповсюдження Windows інсталятора без необхідності наявності встановленого Python у користувача:
```bash
harness-utils build-installer
```
Згенерований інсталятор буде розміщено у `dist/HarnessUtilsInstaller/HarnessUtilsInstaller.exe`.

---

## 🧪 Перевірка якості та тестування

Для перевірки коду запустіть повний комплекс тестування та лінтингу:
```bash
ruff check src tests
mypy src
pytest
```

---

## 📁 Структура проекту

- `src/harness_utils/`
  - `generator.py` - Модуль генерації harness-файлів.
  - `installer/`
    - `script_manager.py` - Сканування, парсинг та додавання нових скриптів.
    - `installer_engine.py` - Ядро встановлення, PATH, ярлики та реєстр Windows.
    - `gui.py` - Graphical Wizard GUI на Tkinter.
    - `builder.py` - Модуль компіляції автономного `.exe` за допомогою PyInstaller.
  - `cli.py` - Головний CLI маршрутизатор та команди.
- `script/` - Наявні скрипти проекту (`create_harness.bat`, `create_harness.ps1`, `install_scripts.bat`, тощо).
- `tests/` - Повний набір unit та integration тестів.
