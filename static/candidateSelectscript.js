const accept=document.querySelector('.accepted');
const reject=document.querySelector('.rejected');
const append=document.querySelector('.texttoadd');
const comment=document.querySelector('.comment');
console.log(accept.value)
accept.addEventListener('click',()=>{// event to send mail asynchronously to candidate that he is selected
    console.log(accept.value)
    fetch('/accept')
    .then(response=>response.text())
    .then((text)=>{
        if(text=='success'){
            alert('Mail Sent succesfully');
        }
        else{
            alert("Mail not sent")
        }
    })
    document.querySelector('#tochange').innerHTML='Selected this candidate';
    reject.disabled=true;
    accept.disabled=true;

})
reject.addEventListener('click',()=>{// event to send mail asynchronously to candidate that he is not selected
    fetch('/reject')
    .then(response=>response.text())
    .then((text)=>{
        if(text=='success'){
            alert('Mail Sent succesfully');
        }
        else{
            alert("Mail not sent")
        }
    })
    document.querySelector('#tochange').innerHTML='Rejected this candidate';
    reject.disabled=true;
    accept.disabled=true;

})
