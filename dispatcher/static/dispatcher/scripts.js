document.addEventListener('DOMContentLoaded', function() {
    const STOP_DINAMIC = document.getElementById('stop_dinamic'); // Элемент перед которым будут вставляться динамические блоки
    const SELECT_DEFAULT_VALUE = "выберите модуль"; // значение select списка по умолчанию
    // ДОБАВЛЕНИЕ НОВОГО БЛОКА МОДУЛЯ ПРИ НАЖАТИИ КНОПКИ +
    let blockCount = 0; // Счетчик блоков
    load_session(); // при загрузке страницы нужно выгрузить данные из сессии


  // ОБНОВЛЕНИЕ ИЗОБРАЖЕНИЙ НА САЙТЕ
  async function update_img(value_request,img_id){
    console.log(value_request);
    var response = await modul_img_update(value_request);
    document.getElementById("modul_img_" + img_id).src = response;
  }



  // CHANGE -> ОБРАБОТКА ЛЮБЫХ ИЗМЕНЕНИЙ НА СТРАНИЦЕ (СМЕНА ЗНАЧЕНИЯ SELECT, УСТАНОВКА ГАЛОЧКИ)
  // Используем делегирование событий
  document.addEventListener('change', async function(event) {
    console.log("изменение select");
    var selectedElement = event.target.closest('select[id^="modul_select_"]'); // Находим ближайший select с id, начинающимся с "my_select_"
    if (selectedElement){
      var selectedId = event.target.id; // Получаем id выделенного селектора
      selectedId = selectedId.split('_')[2]; // извлечение номера идентификатора
      var select_value =  selectedElement.value; // значение выбранного select 
      update_img(select_value,selectedId);
    }
  });


    // ОБНОВЛЕНИЕ SELECT ИЗ СПИСКА МОДУЛЕЙ (ЗАПОЛНЕНИЕ OPTIONS)
    function select_modul_update(select_id,modulList){
      // ЗАПОЛНЕНИЕ SELECT (ВЫПАДАЮЩИЙ СПИСОК) ЗНАЧЕНИЯМИ (OPTIONS)
      var selectElement = document.getElementById('modul_select_'+select_id); // получение объекта select
      console.log(selectElement);
      console.log(select_id);

      // Очистка текущих опций (чтобы значения не задублировались)
      selectElement.innerHTML = '';

      var option = document.createElement('option');
      option.text = SELECT_DEFAULT_VALUE;// заменить на константу полученную из view
      selectElement.add(option);
      // УСТАНОВКА ЗНАЧЕНИЯ SELECT (ВЫБОР OPTIONS ПО УМОЛЧАНИЮ)
      selectElement.value = SELECT_DEFAULT_VALUE; // заменить на константу полученную из view

      modulList.forEach(modul => {
        var option = document.createElement('option');
        console.log(modul.art + " " + modul.name);
        option.text = modul.art.trim() + " " + modul.name.trim();
        selectElement.add(option);
        });
        
    }


    // ЗАГРУЗКА СЕССИИ (ИСПОЛЬЗУЕТСЯ ПРИ ИНИЦИАЛИЗАЦИИ)
    async function load_session() {
      var moduls_from_session = await ajax_get_session(false);
      //console.log("Из сессии получены модули: " + JSON.stringify(moduls_from_session));
      
      for (let i = 0; i < moduls_from_session.length; i++) {
        if (i > 0) {
          await add_block(); // Добавляем новый блок | ВАЖНО: НУЖНО БЫЛО ДОЖДАТЬСЯ ЗАВЕРШЕНИЯ РАБОТЫ ADD BLOCK (AWAIT!!)
          var moduls = await ajax_get_modulsd(); // Получаем значения для заполнения модуль листа
          // Обновляем значения списков только после добавления блока
          select_modul_update(blockCount, moduls);
        }
        
        console.log(moduls_from_session[i].modul.art + " " + moduls_from_session[i].modul.name);
        var block_name = moduls_from_session[i].modul.art + " " + moduls_from_session[i].modul.name;
        var screen = moduls_from_session[i].screen;
        var schine = moduls_from_session[i].schine;
        set_value_block(i, block_name, screen, schine); // Установка значений в блоке
        console.log("Из сессии получен модуль: " + moduls_from_session[i].modul.url_image);
        document.getElementById("modul_img_" + blockCount).src = moduls_from_session[i].modul.url_image;
      }
    }


    // // TEST 2 -> НАЖАТИЕ КНОПКИ TEST2 ОБРАБОТКА
    // document.getElementById('test2').addEventListener('click', async function(event) {
    //   showBootstrapAlert('TEST MESSAGE','hr','message_moduls');
    // }); // ОБРАБОТКА КНОПКИ TEST


    // // TEST 3 -> НАЖАТИЕ КНОПКИ TEST3 ОБРАБОТКА
    // document.getElementById('test3').addEventListener('click', async function(event) {
    // }); // ОБРАБОТКА КНОПКИ TEST


    // AJAX -> ПОЛУЧЕНИЕ СЕССИИ ОТ VIEW.SEND_SESSION / для сброса модулей в сессии используется ключ del_session
    function ajax_get_session(del_session=false,del_key=null){
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
        if(del_key){
          formData.append('session_del_key',del_key);
        }else{
          formData.append('session_del_key','all_reset');
        }
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

    // AJAX -> ПОЛУЧЕНИЕ ИЗОБРАЖЕНИЯ
    function modul_img_update(value_request) {
      return new Promise((resolve, reject) => {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', get_one_modul, true);
        xhr.setRequestHeader('Content-Type', "application/x-www-form-urlencoded");
        xhr.onload = function() {
          if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            console.log(response.url_image);
            resolve(response.url_image); // Возвращаем URL изображения
          } else {
            reject("Произошла ошибка при отправке данных. Пожалуйста попробуйте ещё раз.");
          }
        };

        var formData = new FormData(document.getElementById("form_0"));
        formData.append('value_request', value_request);
        var params = new URLSearchParams(formData).toString();
        xhr.send(params);
      });
    }

    // ОЧИСТКА ПОЛЕЙ NAME PROJECT сброс значений в поле информация о проекте на значения по умолчанию
    document.getElementById('project_name_reset').addEventListener('click', function(event) {
      //alert(JSON.stringify(default_project_name));
      document.getElementById("project_name").placeholder = default_project_name.name;
      document.getElementById("project_name").value = "";
      document.getElementById("ldsp_color").placeholder = default_project_name.ldsp_color;
      document.getElementById("metal_color").value = "";
      document.getElementById("discount").placeholder = default_project_name.discount;
      document.getElementById("discount").value = "";
      ajax_get_session(true,'del_name');
    });


    // ОБРАБОТКА КНОПКИ MODUL RESET "x" СБРОС БЛОКОВ С МОДУЛЯМИ
    document.getElementById('modul_reset').addEventListener('click', async function(event) {
      reset_block();
      update_img(null,0);
    });


    // ОЧИСТКА ПОЛЕЙ МОНИТОРОВ
    document.getElementById('monitor_reset').addEventListener('click', function(event) {
      event.preventDefault(); // отмена стандартного поведения формы

      var monitorTypes = ["monitor_type_1","monitor_type_2","monitor_type_3"]
      for (var i=0; i < monitorTypes.length; i++){
        document.getElementById(monitorTypes[i]).value = 0
      }
      ajax_get_session(true,'del_monitor');
    });


    // ОЧИСТКА ПОЛЕЙ РОЗЕТКИ + МОНИТОРЫ
    document.getElementById('electric_ajax').addEventListener('click', function(event) {
      event.preventDefault(); // отмена стандартного поведения формы
      document.getElementById("electric_power").value = 0;
      document.getElementById("electric_rj45").value = 0;
      ajax_get_session(true,'del_electric');
    });


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
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    }

    // RESET_ALL -> НАЖАТИЕ КНОПКИ TEST ОБРАБОТКА
    document.getElementById('reset_all').addEventListener('click', async function(event) {
      event.preventDefault(); // Отменяем стандартное поведение формы html
      //alert("press btn test");
      var res = await ajax_get_session(true, 'all_reset');
      console.log("Полученные модули: " + JSON.stringify(res));
      window.location.reload();
    }); // ОБРАБОТКА КНОПКИ TEST




    // НАЖАТИЕ НА КНОПКУ ДОБАВЛЕНИЕ НОВОГО БЛОКА МОДУЛЯ 
    document.getElementById('add_block').addEventListener('click', async function(event) {
      var res = await ajax_check_parametrs('is_add_block',blockCount); // отправить тип проверки и параметр
      if(res.is_check){
        await add_block(); // добавляем новый блок (скопированный с нулевого блока)
        var moduls = await ajax_get_modulsd(); // получаем значения для заполнения модуль листа
        select_modul_update(blockCount,moduls); // обновляем значения списков
        set_value_block(blockCount,'выберите модуль','0',false); // устанавливаем значения по умолчанию
        //update_img('reset',blockCount); // устанаваем картинку по умолчанию
      }else{
        console.log('ошибка проверка не пройдена');
        showBootstrapAlert(res.msg,'hr','message_moduls');
      }
    });


    // ОТПРАВКА ДАННЫХ НА СЕРВЕР (ПРОВЕРКА ПОЛЕЙ)
    document.getElementById('modul_send').addEventListener('click', async function(event) {
      event.preventDefault(); // Отменяем стандартное поведение формы html (перехватываем кнопку)
      // проверка формы выполняется здесь //
      var res = await ajax_check_parametrs('is_send_form',blockCount); // отправить тип проверки и параметр
      //alert(JSON.stringify(res));
      if(res.is_check){
        document.getElementById('form_0').submit(); // в ручную отправляем форму на сервер
      }else{
        console.log('ошибка проверка не пройдена');
        showBootstrapAlert(res.msg,'hr','message_moduls');
      }
      // проверка формы выполняется здесь //
    }); // ОБРАБОТКА КНОПКИ TEST


    // СБРОС БЛОКОВ ВЫБОРА МОДУЛЕЙ
    async function reset_block(){
      await ajax_get_session(true,'del_modul'); // удаление сессии (ключ true Добавляет delete_key)
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
      
      const imgElement = newBlock.querySelector(`#modul_img_${blockCount}`);
      var response = await modul_img_update('reset'); // получение картинки из AJAX
      imgElement.src = response;
      //document.getElementById("modul_img_" + img_id).src = response;
      
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