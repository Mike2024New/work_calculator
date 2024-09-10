document.addEventListener('DOMContentLoaded', function() {
    const STOP_DINAMIC = document.getElementById('stop_dinamic'); // Элемент перед которым будут вставляться динамические блоки
    const SELECT_DEFAULT_VALUE = "выберите модуль"; // значение select списка по умолчанию
    // ДОБАВЛЕНИЕ НОВОГО БЛОКА МОДУЛЯ ПРИ НАЖАТИИ КНОПКИ +
    let blockCount = 0; // Счетчик блоков
    load_session(); // при загрузке страницы нужно выгрузить данные из сессии


    // ОБНОВЛЕНИЕ SELECT ИЗ СПИСКА МОДУЛЕЙ (ЗАПОЛНЕНИЕ OPTIONS)
    function select_modul_update(select_id,modulList){
      // ЗАПОЛНЕНИЕ SELECT (ВЫПАДАЮЩИЙ СПИСОК) ЗНАЧЕНИЯМИ (OPTIONS)
      var selectElement = document.getElementById('modul_select_'+select_id); // получение объекта select

      // Очистка текущих опций (чтобы значения не задублировались)
      selectElement.innerHTML = '';

      var option = document.createElement('option');
      option.text = SELECT_DEFAULT_VALUE;// заменить на константу полученную из view
      selectElement.add(option);
      // УСТАНОВКА ЗНАЧЕНИЯ SELECT (ВЫБОР OPTIONS ПО УМОЛЧАНИЮ)
      selectElement.value = SELECT_DEFAULT_VALUE; // заменить на константу полученную из view

      modulList.forEach(modul => {
        var option = document.createElement('option');
        option.text = modul.art + " " + modul.name;
        selectElement.add(option);
        });
        
    }


    // ЗАГРУЗКА СЕССИИ (ИСПОЛЬЗУЕТСЯ ПРИ ИНИЦИАЛИЗАЦИИ)
    async function load_session(){
      var moduls_from_session = await ajax_get_session(false); // получаем значения для заполнения модуль листа
      console.log("Из сессии получены модули" + JSON.stringify(moduls_from_session));
      for(let i=0; i < moduls_from_session.length; i++){
        if (i>0) {
          add_block(); // перенастроить заполнение блоков (нужен актуальный ajax)
          var moduls = await ajax_get_modulsd(); // получаем значения для заполнения модуль листа
          select_modul_update(blockCount,moduls); // обновляем значения списков
        }
      console.log(moduls_from_session[i].modul.art+"  "+moduls_from_session[i].modul.name);
      var block_name = moduls_from_session[i].modul.art+" "+moduls_from_session[i].modul.name;
      var screen = moduls_from_session[i].screen;
      var schine = moduls_from_session[i].schine;
      set_value_block(i,block_name,screen,schine); // установка значений в блоке
      }
    }


    // AJAX -> ПОЛУЧЕНИЕ СЕССИИ ОТ VIEW.SEND_SESSION / для сброса модулей в сессии используется ключ del_session
    function ajax_get_session(del_session=false){
      // AJAX ПОЛУЧЕНИЕ МОДУЛЕЙ ИЗ VIEW dispatcher:get_session
      var xhr = new XMLHttpRequest();
      xhr.open('POST', send_session, true);
      
      // Получение CSRF-токена из cookie
      var csrftoken = document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];
      xhr.setRequestHeader('X-CSRFToken', csrftoken);
      xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    
      // Создаём Promise, который будет возвращать результат AJAX-запроса
      return new Promise((resolve, reject) => {
        xhr.onload = function() {
          if (xhr.status == 200) {
            var response = JSON.parse(xhr.responseText);  
            console.log('ajax запрос модулей прошел успешно');
            resolve(response.session); // Возвращаем модули через resolve
          } else {
            console.log('ajax ошибка запроса на получение модулей');
            reject(xhr.status); // Возвращаем ошибку через reject
          }
        }
    
        xhr.onerror = function() {
          reject(xhr.status); // Возвращаем ошибку через reject в случае ошибки сети
        }
    
        var formData = new FormData(document.getElementById('form_0'));
        formData.append('session_del',del_session);
        var params = new URLSearchParams(formData).toString();
        xhr.send(params);
      });
    }

    // AJAX -> ПОЛУЧЕНИЕ МОДУЛЕЙ ОТ СЕРВЕРА (dispatcher:get_moduls) ЧЕРЕЗ AJAX
    function ajax_get_modulsd() {
      // AJAX ПОЛУЧЕНИЕ МОДУЛЕЙ ИЗ VIEW dispatcher:get_moduls
      var xhr = new XMLHttpRequest();
      xhr.open('POST', getModulsUrl, true);
      
      // Получение CSRF-токена из cookie
      var csrftoken = document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];
      xhr.setRequestHeader('X-CSRFToken', csrftoken);
      xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    
      // Создаём Promise, который будет возвращать результат AJAX-запроса
      return new Promise((resolve, reject) => {
        xhr.onload = function() {
          if (xhr.status == 200) {
            var response = JSON.parse(xhr.responseText);  
            console.log('ajax запрос модулей прошел успешно');
            resolve(response.moduls); // Возвращаем модули через resolve
          } else {
            console.log('ajax ошибка запроса на получение модулей');
            reject(xhr.status); // Возвращаем ошибку через reject
          }
        }
    
        xhr.onerror = function() {
          reject(xhr.status); // Возвращаем ошибку через reject в случае ошибки сети
        }
    
        var formData = new FormData(document.getElementById('form_0'));
        formData.append('dinamic_block_counts',blockCount);
        console.log("отправка запроса при нажатии на +");
        var params = new URLSearchParams(formData).toString();
        xhr.send(params);
      });
    }


    // AJAX -> ПРОВЕРКИ ВВЕДЕННЫХ ЗНАЧЕНИЙ
    function ajax_check_parametrs(send_key,send_value) {
      // AJAX ПОЛУЧЕНИЕ МОДУЛЕЙ ИЗ VIEW dispatcher:get_moduls
      var xhr = new XMLHttpRequest();
      xhr.open('POST', send_for_check, true);
      
      // Получение CSRF-токена из cookie
      var csrftoken = document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];
      xhr.setRequestHeader('X-CSRFToken', csrftoken);
      xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    
      // Создаём Promise, который будет возвращать результат AJAX-запроса
      return new Promise((resolve, reject) => {
        xhr.onload = function() {
          if (xhr.status == 200) {
            var response = JSON.parse(xhr.responseText);  
            console.log('ajax запрос модулей прошел успешно');
            resolve(response.check_info);
          } else {
            console.log('ajax ошибка запроса на получение модулей');
            reject(xhr.status); // Возвращаем ошибку через reject
          }
        }
    
        xhr.onerror = function() {
          reject(xhr.status); // Возвращаем ошибку через reject в случае ошибки сети
        }
    
        var formData = new FormData(document.getElementById('form_0'));
        formData.append(send_key,send_value);
        var params = new URLSearchParams(formData).toString();
        xhr.send(params);
      });
    }


    // HTML -> ОТОБРАЖЕНИЕ ВСПЛЫВАЮЩЕГО СООБЩЕНИЯ НА СТРАНИЦЕ (MESSAGE ALERT)
    function showBootstrapAlert(message,element_type, element_id) {
      /* ВСТАВКА БЛОКА HTML В УКАЗАННОЕ МЕСТО
      message - тело сообщения
      element_type - тип элемента после которого нужно вставить сообщение
      element_id - идентификатор элемента после которого нужно вставить сообщение
      */
      // Создаем HTML для уведомления
      const alertHTML = `
          <div class="alert alert-danger alert-dismissible fade show" role="alert" style="border: 0.01px solid gray;">
              <h6>${message}</h6>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" style="color:white;"></button>
        </div>
      `;
      if(element_type=='hr'){
        const hrElement = document.getElementById(element_id);  // Находим элемент hr
        hrElement.insertAdjacentHTML('afterend', alertHTML); // Вставляем уведомление после элемента hr
      }
    }

    // TEST -> НАЖАТИЕ КНОПКИ TEST2 ОБРАБОТКА
    document.getElementById('test2').addEventListener('click', async function(event) {
      showBootstrapAlert('TEST MESSAGE','hr','message_moduls');
    }); // ОБРАБОТКА КНОПКИ TEST


    // TEST -> НАЖАТИЕ КНОПКИ TEST2 ОБРАБОТКА
    document.getElementById('test3').addEventListener('click', async function(event) {
      var res = await ajax_check_parametrs('is_add_block',blockCount); // отправить тип проверки и параметр
      if(res.is_check){
        console.log('разрешение на действие дано');
        add_block();
      }else{
        console.log('ошибка проверка не пройдена');
        showBootstrapAlert(res.msg,'hr','message_moduls');
      }
      //console.log("AJAX результат: " + JSON.stringify(res));
    }); // ОБРАБОТКА КНОПКИ TEST


    // TEST -> НАЖАТИЕ КНОПКИ TEST ОБРАБОТКА
    document.getElementById('test').addEventListener('click', async function(event) {
      event.preventDefault(); // Отменяем стандартное поведение формы html
      //alert("press btn test");
      var res = await ajax_get_session();
      console.log("Полученные модули: " + JSON.stringify(res));
    }); // ОБРАБОТКА КНОПКИ TEST


    // ОБРАБОТКА КНОПКИ MODUL RESET "x" СБРОС БЛОКОВ С МОДУЛЯМИ
    document.getElementById('modul_reset').addEventListener('click', async function(event) {
      reset_block();
    });


    // СБРОС БЛОКОВ ВЫБОРА МОДУЛЕЙ
    async function reset_block(){
      await ajax_get_session(true); // удаление сессии (ключ true Добавляет delete_key)
      load_session(); // перезагрузить сессию

      for (let i=blockCount; i > 0; i--){
        delete_block();
      }
      set_value_block(0,SELECT_DEFAULT_VALUE,0,false);
    }



    // ДОБАВЛЕНИЕ НОВОГО БЛОКА (ПРОСТО КОПИРУЕТСЯ 0 БЛОК)
    async function add_block() {
      // Клонируем блок
      const newBlock = document.querySelector('.block_0').cloneNode(true);
      
      // Увеличиваем счетчик блоков
      blockCount++;
      
      newBlock.id = `block_${blockCount}`; // Присваиваем новый id для самого блока


      // НУЖНО БУДЕТ УДАЛИТЬ ДУБЛИРУЮЩИЙСЯ КОД
      // Изменяем идентификаторы в клонированном блоке
      newBlock.querySelectorAll('[id]').forEach(element => {
        // Извлекаем номер из id и заменяем его на новый
        const idParts = element.id.split('_'); 
        idParts[idParts.length - 1] = blockCount;
        element.id = idParts.join('_');
      });
    
      // Изменяем name, если это необходимо
      newBlock.querySelectorAll('[name]').forEach(element => {
        const nameParts = element.name.split('_');
        nameParts[nameParts.length - 1] = blockCount; 
        element.name = nameParts.join('_');
      });

      // Изменяем for, если это необходимо
      newBlock.querySelectorAll('label[for]').forEach(element => {
          const forParts = element.htmlFor.split('_'); // Используем htmlFor
          forParts[forParts.length - 1] = blockCount; // Заменяем последний элемент на новый номер
          element.htmlFor = forParts.join('_'); // Присваиваем новое значение
      });
      
      // Вставляем новый блок перед элементом STOP_DINAMIC
      STOP_DINAMIC.insertAdjacentElement('beforebegin', newBlock);
    }


    // УСТАНОВКА ТЕКУЩИХ ЗНАЧЕНИЙ БЛОКА
    async function set_value_block(block_id,select_modul,screen_height,is_shcine){
      /*
      УСТАНОВКА ПАРАМЕТРОВ ДОБАВЛЕННОГО БЛОКА
      select_modul - текущее значение выпадающего меню select
      screen_height - текущее значение radiobutton
      is_shcine  - есть ли шина монтажная
      */
      var badgeElement = document.getElementById('badge_modul_'+block_id);
      badgeElement.textContent = block_id+1; // Присваиваем новое значение (которое будет отображаться на блоках)
      badgeElement.id = `badge_modul_${block_id}`; // Меняем id на новый


      // УСТАНОВКА ТЕКУЩЕГО ЗНАЧЕНИЯ SELECT
      var selectElement = document.getElementById('modul_select_'+block_id); // получение объекта select
      selectElement.value = select_modul; // заменить на константу полученную из view


      // УСТАНАВЛИВАЕМ ТЕКУЩИЙ ПАРАМЕТР ЭКРАНОВ
      var height;

      switch (screen_height) {
        case '45':
          height = '45';
          break;
          case '85':
            height = '85';
            break;
        default:
          height = '0';
      }

      var radioButton = document.getElementById('option_screen_'+ height +'_'+ block_id);
      radioButton.checked = true;


      // СБРАСЫВАЕМ ВЫДЕЛЕНИЕ ГАЛОЧКИ ШИНА МОНТАЖНАЯ
      var checkBox = document.getElementById('select_schine_'+ block_id);
      if (is_shcine){
        checkBox.checked = true;
      }else{
        checkBox.checked = false;
      }
    }


    // НАЖАТИЕ НА КНОПКУ ДОБАВЛЕНИЕ НОВОГО БЛОКА МОДУЛЯ 
    document.getElementById('add_block').addEventListener('click', async function(event) {
      add_block(); // добавляем новый блок (скопированный с нулевого блока)
      var moduls = await ajax_get_modulsd(); // получаем значения для заполнения модуль листа
      select_modul_update(blockCount,moduls); // обновляем значения списков
      set_value_block(blockCount,'выберите модуль','0',false); // устанавливаем значения по умолчанию

    });


    function delete_block(){
      // Находим все блоки с классом 'block_0'
      const blocks = document.querySelectorAll('.block_0');
      
      if (blockCount>0) { // 1 блок удалять нельзя
          // Удаляем последний блок
          const lastBlock = blocks[blocks.length - 1];
          lastBlock.remove(); // Удаляем элемент из DOM
          blockCount--;
      } else {
          console.log('Нет блоков для удаления');
      }
    }


    // УДАЛЕНИЕ ПОСЛЕДНЕГО БОКА МОДУЛЯ
    document.getElementById('minus_block').addEventListener('click', function() {
        // Находим все блоки с классом 'block_0'
        const blocks = document.querySelectorAll('.block_0');
      
        if (blockCount>0) { // 1 блок удалять нельзя
            // Удаляем последний блок
            const lastBlock = blocks[blocks.length - 1];
            lastBlock.remove(); // Удаляем элемент из DOM
            blockCount--;
        } else {
            console.log('Нет блоков для удаления');
        }
    }); // УДАЛЕНИЕ ПОСЛЕДНЕГО БОКА МОДУЛЯ


  });