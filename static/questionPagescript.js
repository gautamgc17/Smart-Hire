'use strict';

/* globals MediaRecorder */

let mediaRecorder;
let recordedBlobs;
let count = 1;
const questions = ['Question 1: Tell something about yourself', 'Question 2: Why should we hire you?', 'Question 3:Where Do You See Yourself Five Years From Now?']
const errorMsgElement = document.querySelector('span#errorMsg');
const recordedVideo = document.querySelector('video#recorded');
const recordButton = document.querySelector('button#record');
const downloadButton = document.querySelector('button#download');
const nextButton = document.getElementById('next');
const time = [];
let userStream;
let filedat;
const numrec=[];


nextButton.addEventListener('click', () => {//Button for next question to be asked
  if (count <= questions.length - 1) {
    document.getElementById('question').innerText = questions[count];
    time.push(Date());
    count++;
    mediaRecorder.stop();
    mediaRecorder.start();
  } else {
    recordButton.disabled = false;
    time.push(Date());
    nextButton.style.display = 'none';
    document.getElementById('question').style.display = 'none';
    count = 1;
    mediaRecorder.stop();
    mediaRecorder.start();
  }
})

recordButton.addEventListener('click', () => {// to start the camera for recording
  if (recordButton.textContent === 'Record') {
    time.push(Date());
    console.log(time);
    startRecording();
  } else {
    stopRecording();
    time.push(Date());
    recordButton.textContent = 'Record';
    downloadButton.disabled=false
  }
});

// playButton.addEventListener('click', () => {
//   const superBuffer = new Blob(recordedBlobs, {type: 'video/webm'});
//   recordedVideo.src = null;
//   recordedVideo.srcObject = null;
//   recordedVideo.src = window.URL.createObjectURL(superBuffer);
//   recordedVideo.controls = true;
//   recordedVideo.play();
// });

downloadButton.addEventListener('click', () => {// send data to server 
  var data = new FormData();
  recordedBlobs.forEach((blob,index) => {
    const arr=[];
    arr.push(blob);
    if(index<3){
      const blobdata=new Blob(arr,{type:'video/webm'});
      data.append(`question${index+1}`,blobdata);
    }
  });


  
  const url1 = `/recorded`;
  fetch(`${window.origin}/analysis`, {
    method: 'POST',
    body: data
  })
    .then(response => {
      console.log(response);
      return response.text()
    })
    .then(data => {
      console.log(data)
      console.log(time);
      if (data === 'success') {
        const a = document.createElement('a');
        a.style.display = 'none';
        a.target = '_self';
        a.href = url1;
        document.body.appendChild(a);
        a.click();
      }
      else {
        alert("can't post");
      }

 
 
    })
});

function handleDataAvailable(event) {// push data to blob or video data
  console.log('handleDataAvailable', event);
  if (event.data && event.data.size > 0) {
    recordedBlobs.push(event.data);
  }
}
function showNextBtn() {
  document.getElementById('next').style.display = 'block';
  document.getElementById('question').innerText = questions[0];
  recordButton.disabled = true;

}
function startRecording() {// start camera
  showNextBtn();
  recordedBlobs = [];
  let options = { mimeType: 'video/webm;codecs=vp9,opus',audioBitsPerSecond:128000,videoBitsPerSecond:2500000 };
  try {
    mediaRecorder = new MediaRecorder(userStream, options);
  } catch (e) {
    console.error('Exception while creating MediaRecorder:', e);
    errorMsgElement.innerHTML = `Exception while creating MediaRecorder: ${JSON.stringify(e)}`;
    return;
  }

  console.log('Created MediaRecorder', mediaRecorder, 'with options', options);
  recordButton.textContent = 'Stop Recording';
  downloadButton.disabled = true;
  mediaRecorder.onstop = (event) => {
    console.log('Recorder stopped: ', event);
    console.log('Recorded Blobs: ', recordedBlobs);
  };
  
  mediaRecorder.ondataavailable = handleDataAvailable;
  mediaRecorder.start();
  console.log('MediaRecorder started', mediaRecorder);
}

function stopRecording() {// stop recording answered question
  console.log('iniside stop');
  console.log(userStream);
  mediaRecorder.stop();
  recordButton.style.display = 'none';
  const gumVideo = document.querySelector('video#gum');
  userStream.getTracks()[0].enabled=false;
  userStream.getTracks()[1].enabled=false;
  // console.log(userStream);
  // delete userStream.getTracks()[0];
  // delete userStream.getTracks()[1];

  // gumVideo.pause();
  // gumVideo.src='';
  // gumVideo.style.display='none';

}

function handleSuccess(stream) {// set video stream to video tag
  recordButton.disabled = false;
  console.log('getUserMedia() got stream:', stream);
  

  const gumVideo = document.querySelector('video#gum');
  gumVideo.srcObject = stream;
}

async function init(constraints) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    userStream = stream;
    handleSuccess(stream);
  } catch (e) {
    console.error('navigator.getUserMedia error:', e);
    errorMsgElement.innerHTML = `navigator.getUserMedia error:${e.toString()}`;
  }
}

document.querySelector('button#start').addEventListener('click', async () => {// start button to trigger camera
  const hasEchoCancellation = document.querySelector('#echoCancellation').checked;
  const hasnoiseSuppression = document.querySelector('#noiseSuppression').checked;
  const hasAutoGainControl = document.querySelector('#autogaincontrol').checked;
  console.log(hasEchoCancellation);
  console.log(hasnoiseSuppression);
  console.log(hasAutoGainControl);
  document.querySelector('button#start').style.display = 'none';
  const constraints = {
    audio: {
      echoCancellation: { exact: hasEchoCancellation },
      autoGainControl:{exact:hasAutoGainControl},
      noiseSupperssion:{exact:hasnoiseSuppression}
    },
    video: {
      width: 1280, height: 720
    }
  };
  console.log('Using media constraints:', constraints);
  await init(constraints);
});