document.addEventListener('DOMContentLoaded',()=>{
  const toggle=document.querySelector('.menu-toggle');
  toggle?.addEventListener('click',()=>document.querySelector('.navlinks')?.classList.toggle('open'));
  document.querySelectorAll('form[data-validate]').forEach(form=>{
    const check=input=>{
      const val=input.value.trim();let message='';
      if(!val)message='Заполните это поле';
      else if(input.name==='login'&&!/^[a-zA-Z0-9_]{3,20}$/.test(val))message='Логин: от 3 до 20 латинских символов';
      else if(input.name==='password'&&(val.length<8||val.length>128))message='Пароль: 8–128 символов';
      else if(input.name==='full_name'&&val.length<3)message='ФИО: минимум 3 символа';
      else if(input.name==='email'&&!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(val))message='Проверьте адрес электронной почты';
      else if(input.name==='phone'&&val.replace(/\D/g,'').length!==11)message='Проверьте телефон';
      const output=input.parentElement.querySelector('.field-error');if(output)output.textContent=message;
      input.classList.toggle('invalid',!!message);return !message;
    };
    form.querySelectorAll('input:not([type=hidden])').forEach(input=>input.addEventListener('blur',()=>check(input)));
    form.addEventListener('submit',e=>{let ok=true;form.querySelectorAll('input:not([type=hidden])').forEach(input=>{if(!check(input))ok=false});if(!ok)e.preventDefault()});
  });
});
