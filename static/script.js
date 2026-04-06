document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('generator-form');
    const gradeSelect = document.getElementById('grade');
    const semesterSelect = document.getElementById('semester');
    const chapterSelect = document.getElementById('chapter');
    const lessonSelect = document.getElementById('lesson');
    const countInput = document.getElementById('count');
    
    const resultContainer = document.getElementById('result-container');
    const examContent = document.getElementById('exam-content');
    const btnText = document.querySelector('.btn-text');
    const loader = document.getElementById('loader');
    const generateBtn = document.getElementById('generate-btn');
    const exportPdfBtn = document.getElementById('export-pdf-btn');

    let curriculumData = null;

    // Tải dữ liệu giáo trình
    try {
        const response = await fetch('/static/curriculum.json');
        curriculumData = await response.json();
        updateChapters(); // Khởi tạo ban đầu
    } catch (err) {
        console.error("Không thể tải giáo trình:", err);
    }

    function updateChapters() {
        const grade = gradeSelect.value;
        const semester = semesterSelect.value;
        
        chapterSelect.innerHTML = '';
        if (curriculumData && curriculumData[grade] && curriculumData[grade][semester]) {
            const chapters = curriculumData[grade][semester];
            chapters.forEach((ch, index) => {
                const option = document.createElement('option');
                option.value = index;
                option.textContent = ch.chapter;
                chapterSelect.appendChild(option);
            });
            updateLessons();
        }
    }

    function updateLessons() {
        const grade = gradeSelect.value;
        const semester = semesterSelect.value;
        const chapterIdx = chapterSelect.value;

        lessonSelect.innerHTML = '';
        if (curriculumData && curriculumData[grade] && curriculumData[grade][semester] && curriculumData[grade][semester][chapterIdx]) {
            const lessons = curriculumData[grade][semester][chapterIdx].lessons;
            lessons.forEach(lesson => {
                const option = document.createElement('option');
                option.value = lesson;
                option.textContent = lesson;
                lessonSelect.appendChild(option);
            });
        }
    }

    gradeSelect.addEventListener('change', updateChapters);
    semesterSelect.addEventListener('change', updateChapters);
    chapterSelect.addEventListener('change', updateLessons);

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const grade = gradeSelect.value;
        const semester = semesterSelect.value;
        const chapter = chapterSelect.options[chapterSelect.selectedIndex].text;
        const lesson = lessonSelect.value;
        const count = countInput.value;

        // Xác định loại đề
        let testType = 'lesson';
        if (lesson.toLowerCase().includes('luyện tập chung')) {
            testType = 'chapter';
        } else if (lesson.toLowerCase().includes('đề ôn tập học kì')) {
            testType = 'semester';
        }

        // Cập nhật trạng thái loading
        btnText.textContent = 'Đang soạn đề...';
        loader.classList.remove('hidden');
        generateBtn.disabled = true;
        resultContainer.classList.add('hidden');

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    grade, semester, chapter, lesson, test_type: testType, count: parseInt(count)
                })
            });

            const data = await response.json();

            if (response.ok && data.html) {
                examContent.innerHTML = data.html;
                
                // Reset nút hiển thị đáp án
                const toggleAnswerBtn = document.getElementById('toggle-answer-btn');
                if (toggleAnswerBtn) {
                    toggleAnswerBtn.innerHTML = '👁️ Hiện Đáp Án';
                }
                
                resultContainer.classList.remove('hidden');
                resultContainer.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert("Lỗi: " + (data.error || "Không rõ nguyên nhân"));
            }
        } catch (err) {
            alert("Lỗi kết nối máy chủ");
        } finally {
            btnText.textContent = 'Tạo Đề Ngay 🚀';
            loader.classList.add('hidden');
            generateBtn.disabled = false;
        }
    });

    // Bật tắt hiển thị đáp án
    const toggleAnswerBtn = document.getElementById('toggle-answer-btn');
    if (toggleAnswerBtn) {
        toggleAnswerBtn.addEventListener('click', () => {
            const answerKey = document.querySelector('.answer-key');
            if (answerKey) {
                if (answerKey.style.display === 'none' || !answerKey.style.display) {
                    answerKey.style.display = 'block';
                    toggleAnswerBtn.innerHTML = '🙈 Ẩn Đáp Án';
                } else {
                    answerKey.style.display = 'none';
                    toggleAnswerBtn.innerHTML = '👁️ Hiện Đáp Án';
                }
            } else {
                alert('Không tìm thấy phần đáp án trong đề thi này!');
            }
        });
    }

    // Xuất PDF
    exportPdfBtn.addEventListener('click', () => {
        const element = document.getElementById('exam-content');
        const opt = {
            margin:       10,
            filename:     `De_On_Tap_Toan_Lop_${gradeSelect.value}_Ky_${semesterSelect.value}.pdf`,
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2 },
            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };
        html2pdf().set(opt).from(element).save();
    });
});
