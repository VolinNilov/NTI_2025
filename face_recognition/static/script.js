async function startFaceAuth() {
    // Показываем секцию камеры
    toggleCameraSection(true);

    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        await new Promise(resolve => video.onloadedmetadata = resolve);
        video.play();

        setTimeout(async () => {
            const context = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            // Преобразование в base64
            const image = canvas.toDataURL('image/jpeg');
            // Отправка на сервер
            const response = await fetch('/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image })
            });
            const result = await response.json();
            if (result.user) {
                alert(`Добро пожаловать, ${result.user}!`);
            } else {
                alert('Ошибка: ' + (result.error || 'Неизвестная ошибка'));
            }
            // Остановка камеры
            stream.getTracks().forEach(track => track.stop());
        }, 3000);
    } catch (err) {
        console.error('Ошибка доступа к камере:', err);
        alert('Не удалось получить доступ к камере');
        toggleCameraSection(false);
    }
}