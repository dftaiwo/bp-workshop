$(document).ready(function() {
    const dropArea = $('#drop-area');
    const fileInput = $('#file-upload');
    const imagePreview = $('#image-preview');
    const clearImagesLink = $('#clear-images');
    const clearImagesContainer = $('#clear-images-container');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.on(eventName, preventDefaults);
        $('body').on(eventName, preventDefaults);
    });

    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.on(eventName, highlight);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.on(eventName, unhighlight);
    });

    // Handle dropped files
    dropArea.on('drop', handleDrop);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight() {
        dropArea.addClass('border-blue-500');
    }

    function unhighlight() {
        dropArea.removeClass('border-blue-500');
    }

    function handleDrop(e) {
        const dt = e.originalEvent.dataTransfer;
        const files = dt.files;
        fileInput[0].files = files;
        handleFiles(files);
    }

    function handleFiles(files) {
        imagePreview.empty();
        if (files.length > 0) {
            imagePreview.removeClass('hidden');
            clearImagesContainer.removeClass('hidden');
            Array.from(files).forEach(file => {
                displayPreview(file);
            });
        } else {
            imagePreview.addClass('hidden');
            clearImagesContainer.addClass('hidden');
        }
    }

    function displayPreview(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = $('<img>').attr({
                'src': e.target.result,
                'class': 'max-w-full max-h-[150px] w-auto h-auto object-contain rounded-lg'
            });
            imagePreview.append(img);
        }
        reader.readAsDataURL(file);
    }

    fileInput.change(function() {
        handleFiles(this.files);
    });

    $('#upload-form').submit(function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        
        $('#result').html('');
        $('#progress-bar').removeClass('hidden');
        
        let progress = 0;
        const interval = setInterval(function() {
            progress += 5;
            if (progress > 95) {
                clearInterval(interval);
            }
            $('#progress').css('width', progress + '%');
            $('#progress-text').text('Analysing... ' + progress + '%');
        }, 500);

        $.ajax({
            url: '/analyze',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(data) {
                clearInterval(interval);
                $('#progress').css('width', '100%');
                $('#progress-text').text('Analysis complete!');
                
                setTimeout(function() {
                    $('#progress-bar').addClass('hidden');
                    if (data.error) {
                        $('#result').html(`<p class="text-red-500">${data.error}</p>`);
                    } else {
                        $('#result').html(`<p class="text-green-600 font-semibold">Analysis Result:</p><pre class="mt-2 bg-gray-100 p-2 rounded"><code>${JSON.stringify(JSON.parse(data.result), null, 2)}</code></pre>`);
                    }
                }, 500);
            },
            error: function(xhr, status, error) {
                clearInterval(interval);
                $('#progress-bar').addClass('hidden');
                $('#result').html(`<p class="text-red-500">An error occurred: ${error}</p>`);
            }
        });
    });

    clearImagesLink.click(function(e) {
        e.preventDefault();
        clearImages();
    });

    function clearImages() {
        fileInput.val('');
        imagePreview.empty().addClass('hidden');
        clearImagesContainer.addClass('hidden');
    }
});
