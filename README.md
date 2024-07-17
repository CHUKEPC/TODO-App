# TODO List by CHUKEPC

TODO List by CHUKEPC - это простое и эффективное приложение для управления задачами, разработанное на Python с использованием библиотеки Tkinter.

## Описание проекта

Это приложение позволяет пользователям создавать, редактировать и отслеживать свои задачи. Основные функции включают:

- Добавление новых задач с указанием приоритета и срока выполнения
- Отображение активных и выполненных задач в отдельных списках
- Возможность отметить задачу как выполненную или отменить выполнение
- Редактирование существующих задач
- Удаление задач
- Сортировка задач по названию, приоритету или сроку выполнения
- Автоматическое создание ярлыка на рабочем столе при первом запуске

## Установка

1. Убедитесь, что у вас установлен Python 3.6 или выше.
2. Склонируйте репозиторий:
```
git clone https://github.com/ваш-username/todo-list-by-chukepc.git
```
3. Перейдите в директорию проекта:
```
cd todo-list-by-chukepc
```
4. Установите необходимые зависимости:
```
pip install -r requirements.txt
```
## Использование

1. Запустите приложение:
```
python main.py
```
или дважды щелкните на файл `TODO_App.exe`, если вы используете исполняемый файл.

2. Для добавления новой задачи:
- Введите текст задачи в поле ввода
- Выберите приоритет из выпадающего списка
- Установите срок выполнения с помощью календаря
- Нажмите кнопку "Добавить задачу"

3. Для управления существующими задачами:
- Щелкните правой кнопкой мыши на задаче для вызова контекстного меню
- Выберите нужное действие (отметить выполненной, редактировать, удалить)

4. Для сортировки задач:
- Щелкните на заголовок столбца в списке задач

## Требования

- Python 3.6+
- tkinter
- tkcalendar
- sqlite3
- winshell (для Windows)
- win32com (для Windows)

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности см. в файле [LICENSE](LICENSE).

## Автор

CHUKEPC

## Поддержка

Если у вас возникли проблемы или есть предложения по улучшению, пожалуйста, создайте issue в этом репозитории.