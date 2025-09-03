"""
  Copyright (c) 2016- 2025, Wiliot Ltd. All rights reserved.

  Redistribution and use of the Software in source and binary forms, with or without modification,
   are permitted provided that the following conditions are met:

     1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     2. Redistributions in binary form, except as used in conjunction with
     Wiliot's Pixel in a product or a Software update for such product, must reproduce
     the above copyright notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the distribution.

     3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
     may be used to endorse or promote products or services derived from this Software,
     without specific prior written permission.

     4. This Software, with or without modification, must only be used in conjunction
     with Wiliot's Pixel or with Wiliot's cloud service.

     5. If any Software is provided in binary form under this license, you must not
     do any of the following:
     (a) modify, adapt, translate, or create a derivative work of the Software; or
     (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
     discover the source code or non-literal aspects (such as the underlying structure,
     sequence, organization, ideas, or algorithms) of the Software.

     6. If you create a derivative work and/or improvement of any Software, you hereby
     irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
     royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
     right and license to reproduce, use, make, have made, import, distribute, sell,
     offer for sale, create derivative works of, modify, translate, publicly perform
     and display, and otherwise commercially exploit such derivative works and improvements
     (as applicable) in conjunction with Wiliot's products and services.

     7. You represent and warrant that you are not a resident of (and will not use the
     Software in) a country that the U.S. government has embargoed for use of the Software,
     nor are you named on the U.S. Treasury Department’s list of Specially Designated
     Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
     You must not transfer, export, re-export, import, re-import or divert the Software
     in violation of any export or re-export control laws and regulations (such as the
     United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
     and use restrictions, all as then in effect

   THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
   OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
   WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
   QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
   IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
   ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
   OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
   FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
   (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
   (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
   (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
   (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""

lang_map = {
            'English': 'En',
            'Russian': 'Ru',
            'Hebrew': 'He'
        }

moh_instruction = {
    "Missing Label": {
        "En": [
            "* Please check if there is a missing label case, if not:",
            "    * disconnect and reconnect Arduino",
            "    * check R2R Controller",
            "    * press continue",
            "* Please add a faulty tag inside of the missing label",
            "* Make sure the label on the test site is centered, and click on continue"
        ],
        "Ru": [
            "* Пожалуйста, проверьте, отсутствует ли этикетка",
            "* если нет:",
            "*      Отключите и снова подключите контроллер - Arduino",
            "*      Проверьте настройки контроллера и машины:",
            "*      Нажмите продолжить",
            "* если да:",
            "*      Пожалуйста, добавьте дефектнаю этикетку вместо пустого",
            "*      Убедитесь, что этикетка на тестовом сайте расположена по центру, затем нажмите Продолжить"
        ],
        "He": [
            "*אנא בדוק אם חסרה תווית ",
            "במידה ולא:",
            "נתק וחבר מחדש את הבקר - ארדוינו",
            "בדוק את הבקר והגדרות המכונה",
            "במידה וכן:",
            "*הוסף תווית פגומה במקום שבו חסר",
            "* ודא שהתווית על מקום הבדיקה ממורכזת",
            "*לחץ על המשך"
        ]
    },
    "stop Criteria": {
        "En": [
            "* Please make sure reel is above coupler",
            "* Check antennas connections",
            "* Check test configurations"
        ],
        "Ru": [
            "* Пожалуйста, убедитесь, что лента находится над тестовой антенной",
            "* проверьте подключение антенны",
            "* Проверьте правильные настройки"
        ],
        "He": [
            "* אנא וודא כי הסרט נמצא מעל האנטנת בדיקה",
            "*                     בדוק חיבורי אנטנות",
            "*                     בדוק תקינות הגדרות"
        ]
    },
    "Validation Failed": {
        "En": [
            "* Please check printed label",
            "* If label is correct, please take a picture and send to Wiliot team",
            "* If label is incorrect (different external, black square instead of external id and vice versa):",
            "    * please check the step size in the R2R machine",
            "    * please check the the R2R controller for any errors",
            "    * please press on STOP",
            "* Replace label with a faulty label",
            "* Clean printer and scanner",
            "* Restart printer and scanner if available",
            "* Click on continue after printer and scanner are alive",
            "* If REEL_ID_LIMIT_EXCEEDED, please contact Wiliot Support"
        ],
        "Ru": [
            "* Пожалуйста, проверьте напечатанную этикетку",
            "* Если этикетка правильная, сделайте фото и отправьте к Wiliot",
            "* Если есть ошибка несоответствия (ожидается одна этикетку, но проверяется другая этикетка): ",
            "       * проверьте размер шага на машине R2R",
            "       * Проверьте, нет ли ошибок в машине",
            "       * Oстановить бег",
            "* Замените этикетку на дефектнаю этикетку",
            "* очистите принтер и сканер",
            "* Запустите принтер и сканер, если это возможно",
            "* Нажмите продолжить после включения принтера и сканера и проверки их работоспособности",
            "* Если вы получили REEL_ID_LIMIT_EXCEEDED, пожалуйста, свяжитесь с командой поддержки Wiliot"
        ],
        "He": [
            "*אנא בדוק את התווית שהודפסה",
            "*אם התווית נכונה, אנא צלם ושלח לצוות התמיכה",
            "* אם יש שגיאת חוסר התאמה (צפי לתווית אחת אבל נבדקה תווית אחרת):  ",
            "בדוק את גודל הצעד במכונה",
            "בדוק האם ישנם שגיאות במכונה",
            "עצור את הריצה",
            "*החלף את התווית בתווית פגומה",
            "*נקה את המדפסת והסורק",
            "*אתחל את המדפסת והסורק אם יש זמינות",
            "*לחץ על המשך לאחר הפעלת המדפסת והסורק ובדיקת תקינות",
            "*אם קיבלת REEL_ID_LIMIT_EXCEEDED, אנא צור קשר עם צוות התמיכה של Wiliot"
        ]
    },

    "Files Error": {
        "En": [
            "Please make sure all CSV files are closed"
        ],
        "Ru": [
            "Пожалуйста, убедитесь, что все файлы, такие как EXCEL, закрыты"
        ],
        "He": [
            "אנא וודא כי כל הקבצים סגורים כגון אקסל"
        ]
    },
    "Missed Printing": {
        "En": [
             "* Please check printer error and hard reset the printer by the ON/OFF button",
             "* Stop the run and replace all tags from the empty tag, included till the end of the run with faulty tags"
        ],
        "Ru": [
            "*Проверьте ошибку принтера и выполните полную перезагрузку принтера с помощью 	кнопки ВКЛ/ВЫКЛ",
            "*Остановить бег и заменить все этикетки из пустого тега, "
            "включенные до конца прогона, на неисправные этикетки"
        ],
        "He": [
            "* אנא בדוק את השגיאה במדפסת וטפל בה. לאחר מכן אתחל את המדפסת באמצעות מתג ההפעלה הידני.",
            "* עצור את הריצה והחלף את כלל התגים מהתג הריק, כולל, עד סיום הריצה בתגי דמה (ריבוע שחור)"
        ]
    },

    "Printer Error": {
        "En": [
             "Please hard reset the printer by the ON/OFF button and click continue after printer is alive"
        ],
        "Ru": [
            "Пожалуйста, перезагрузить принтер через кнопку включения, "
            "подождите несколько секунд и нажмите продолжить после запуска принтера»"
        ],
        "He": [
            "אנא אתחל את המדפסת על ידי מתג ההפעלה הידני, המתן מספר רגעים ולחץ על המשך לאחר הפעלת המדפסת"
        ]
    },

    "Scanner Error": {
        "En": [
            "Please disconnect and reconnect the scanner and click continue after 5 seconds when it is alive"
        ],
        "Ru": [
            "Пожалуйста, отключите и снова подключите сканер и нажмите продолжить через 5 секунд после его включения"
        ],
        "He": [
            "אנא נתק וחבר מחדש את הסורק ולחץ על המשך 5 שניות לאחר שנדלק"
        ]
    },

    "Arduino Error": {
        "En": [
            "Please disconnect and reconnect Arduino and click continue after 5 second is alive"
        ],
        "Ru": [
            "Пожалуйста, отключите и снова подключите контроллер - "
            "Arduino и нажмите продолжить через 5 секунд после его включения"
        ],
        "He": [
            "אנא נתק וחבר מחדש את הבקר ה-Arduino ולחץ על המשך 5 שניות לאחר שנדלק"
        ]
    },

    "Gateway Error": {
        "En": [
            "Please disconnect and reconnect Gateway and click continue after 5 second is alive"
        ],
        "Ru": [
            "Пожалуйста, отключите и снова подключите контроллер - "
            "Gateway и нажмите продолжить через 5 секунд после его включения"
        ],
        "He": [
            "אנא נתק וחבר מחדש את הבקר ה-Gateway ולחץ על המשך 5 שניות לאחר שנדלק"
        ]
    },

    "Server Error": {
        "En": [
            "There is a server error, please check your internet connection and try again."
            "If the problem persists, please contact Wiliot Support",
        ],
        "Ru": [
            "Произошла ошибка сервера, пожалуйста, проверьте подключение к интернету и повторите попытку."
            "Если проблема не исчезнет, пожалуйста, свяжитесь с командой поддержки Wiliot"
        ],
        "He": [
            "ישנה שגיאת שרת, אנא בדוק את חיבור האינטרנט שלך ונסה שוב. "
            "אם הבעיה נמשכת, אנא צור קשר עם צוות התמיכה של Wiliot"
        ]
    },

    "General Error": {
        "En": [
            "* Please make sure there are no empty tags after printer. If there are, please replace with faulty tags",
            "* If running with scanner, please make sure all passed tags were scanned by the scanner. "
            "  If there are, please replace with faulty tags the above external id if relevant",
            "* Please follow error instruction, if error is unclear please contact Wiliot Support"
        ],
        "Ru": [
            "* Проверьте, есть ли после принтера пустые этикетки, если да, замените с дефектные этикетки",
            "* Если машина работает со сканером штрих-кода, убедитесь, что все напечатанные этикетки проверены под ним",
            "  Если есть этикетки, которые не были протестированы - "
            "пожалуйста, замените распечатанные этикетки с дефектные этикетки",
            "* Пожалуйста, следуйте инструкциям по ошибке, если инструкции по ошибке непонятны, обратитесь с Wiliot"
        ],
        "He": [
            "*בדוק האם ישנם תגים ריקים לאחר המדפסת, במידה וכן אנא החלף בתגי דמה",
            "*במידה והמכונה עובדת עם סורק ברקודים, וודא כי כל התגים המודפסים עברו בדיקה תחתיו",
            "במידה וישנם תגים שלא עברו בדיקה - אנא החלף תגים מודפסים בתגי דמה (תגים שלא נבדקו)",
            "*אנא פעל לפי ההוראות השגיאה, אם הוראות השגיאה אינן ברורות, אנא צור קשר עם צוות התמיכה"
        ]
    }
}

if __name__ == '__main__':
    scanned_data = 'a0eT0826'
    pass