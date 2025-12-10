import React, { useState, useEffect, useRef } from "react";
import { ChevronDown, ChevronUp, Check } from "lucide-react";

/* Inline SVG icons to avoid dependency issues */
const RobotIcon = ({ className = "w-5 h-5", ariaLabel = "robot" }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    aria-label={ariaLabel}
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect
      x="3"
      y="7"
      width="18"
      height="10"
      rx="2"
      stroke="currentColor"
      strokeWidth="1.5"
      fill="none"
    />
    <rect
      x="7"
      y="3"
      width="4"
      height="4"
      rx="1"
      stroke="currentColor"
      strokeWidth="1.5"
      fill="none"
    />
    <circle cx="9" cy="12" r="0.9" fill="currentColor" />
    <circle cx="15" cy="12" r="0.9" fill="currentColor" />
    <rect x="10.5" y="16" width="3" height="1" rx="0.5" fill="currentColor" />
  </svg>
);

const UserIcon = ({ className = "w-5 h-5", ariaLabel = "user" }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    aria-label={ariaLabel}
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle
      cx="12"
      cy="8"
      r="3"
      stroke="currentColor"
      strokeWidth="1.5"
      fill="none"
    />
    <path
      d="M4 20c1.333-4 6-6 8-6s6.667 2 8 6"
      stroke="currentColor"
      strokeWidth="1.5"
      fill="none"
      strokeLinecap="round"
    />
  </svg>
);

/* Theme colors */
const PRIMARY = "#347dc6";
const BG = "#F6F8FD";

// Tambahkan style untuk hover via CSS-in-JS agar aman
const answerButtonBase =
  "w-full text-left px-3 py-2 rounded-lg border flex items-center gap-3 text-base transition-colors duration-200";

const ChatApp = () => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [stage, setStage] = useState("welcome");
  const [selectedNSoal, setSelectedNSoal] = useState(0);
  const [questions, setQuestions] = useState([]);
  const [metadata, setMetadata] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [showButtons, setShowButtons] = useState(false);
  const [expandedProdi, setExpandedProdi] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const messagesEndRef = useRef(null);
  const hasInitialized = useRef(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, showButtons]);

  const addBotMessage = (text, delay = 0, showChoicesAfter = false) => {
    setShowButtons(false);
    setTimeout(() => {
      setIsTyping(true);
      setTimeout(() => {
        setMessages((prev) => [...prev, { type: "bot", text }]);
        setIsTyping(false);
        if (showChoicesAfter) {
          setTimeout(() => setShowButtons(true), 700);
        }
      }, 900);
    }, delay);
  };

  const addUserMessage = (text) => {
    setMessages((prev) => [...prev, { type: "user", text }]);
  };

  useEffect(() => {
    if (!hasInitialized.current) {
      hasInitialized.current = true;
      addBotMessage(
        "Selamat datang di Sistem Rekomendasi Program Studi JTI Polindra.\nSilakan pilih jumlah pertanyaan yang ingin kamu jawab:",
        0,
        true
      );
    }
  }, []);

  const handleNSoalSelect = async (n, label) => {
    setShowButtons(false);
    setSelectedAnswer(label);

    setTimeout(async () => {
      addUserMessage(label);
      setSelectedAnswer(null);
      setSelectedNSoal(n);
      setStage("loading_questions");

      addBotMessage("Menyiapkan pertanyaan...", 400, false);

      setTimeout(async () => {
        try {
          const response = await fetch(
            "http://localhost:5000/api/get-questions",
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ n_soal: n }),
            }
          );

          const data = await response.json();

          if (data.soal?.length > 0) {
            setQuestions(data.soal);
            setMetadata(data.metadata);
            setStage("quiz");
            addBotMessage(
              `Pertanyaan 1/${data.soal.length}\n\n${data.soal[0].pertanyaan}`,
              400,
              true
            );
            setCurrentQuestion(0);
          } else {
            addBotMessage(
              "Maaf, tidak ada soal yang tersedia. Silakan refresh halaman.",
              400,
              false
            );
          }
        } catch (error) {
          console.error("Error fetching questions:", error);
          addBotMessage(
            "Terjadi kesalahan saat mengambil soal. Silakan coba lagi nanti.",
            400,
            false
          );
        }
      }, 800);
    }, 160);
  };

  const handleAnswerSelect = async (option, text) => {
    setShowButtons(false);
    setSelectedAnswer(`${option}. ${text}`);

    setTimeout(() => {
      addUserMessage(`${option}. ${text}`);
      setSelectedAnswer(null);
      const newAnswers = [...answers, option];
      setAnswers(newAnswers);

      setTimeout(() => {
        if (currentQuestion < questions.length - 1) {
          const nextQ = currentQuestion + 1;
          setCurrentQuestion(nextQ);
          addBotMessage(
            `Pertanyaan ${nextQ + 1}/${questions.length}\n\n${
              questions[nextQ].pertanyaan
            }`,
            700,
            true
          );
        } else {
          setStage("calculating");
          addBotMessage(
            "Terima kasih. Sedang menganalisis jawabanmu...",
            500,
            false
          );

          setTimeout(async () => {
            try {
              const response = await fetch(
                "http://localhost:5000/api/rekomendasi",
                {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                    jawaban: newAnswers,
                    metadata,
                    n_soal: selectedNSoal,
                  }),
                }
              );

              const data = await response.json();

              if (data.rekomendasi) {
                setStage("result");
                displayResults(data.rekomendasi);
              } else {
                addBotMessage(
                  "Terjadi kesalahan saat memproses hasil. Mohon coba lagi.",
                  500,
                  false
                );
              }
            } catch (error) {
              console.error("Error submitting answers:", error);
              addBotMessage(
                "Terjadi kesalahan saat mengirim jawaban. Mohon coba lagi.",
                500,
                false
              );
            }
          }, 1000);
        }
      }, 500);
    }, 160);
  };

  const formatBoldText = (text) => {
    const parts = String(text).split(/(\*\*.*?\*\*)/g);
    return parts.map((part, idx) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong
            key={idx}
            style={{ color: PRIMARY }}
            className="font-semibold"
          >
            {part.slice(2, -2)}
          </strong>
        );
      }
      return part;
    });
  };

  const displayResults = (rekomendasi) => {
    const fullResultMessage = {
      type: "bot",
      isResults: true,
      text: "Analisis selesai. Berikut hasil kecocokan program studi (urut dari yang paling sesuai):",
      data: rekomendasi,
    };
    setTimeout(() => {
      setMessages((prev) => [...prev, fullResultMessage]);
    }, 900);
  };

  const TypingIndicator = () => (
    <div className="flex items-start gap-3 mb-3">
      <div
        style={{ background: PRIMARY }}
        className="w-9 h-9 rounded-full flex items-center justify-center text-white flex-shrink-0"
      >
        <RobotIcon className="w-4 h-4" />
      </div>
      <div
        className="bg-white rounded-2xl px-3 py-2 border"
        style={{ borderColor: "#e6eef9" }}
      >
        <div className="flex gap-1">
          <div
            className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
            style={{ animationDelay: "0ms" }}
          />
          <div
            className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
            style={{ animationDelay: "120ms" }}
          />
          <div
            className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
            style={{ animationDelay: "240ms" }}
          />
        </div>
      </div>
    </div>
  );

  const ResultCard = ({ text, data }) => {
    const topProdi =
      data && data.length > 0 ? data[0] : { nama: "Program Studi" };
    return (
      <div className="w-full space-y-4">
        {/* Tampilkan teks analisis */}
        <p className="text-slate-800 text-base">{text}</p>

        {/* Judul hasil rekomendasi */}
        <p className="text-slate-800 text-base">
          Berdasarkan jawabanmu, rekomendasi program studi yang sesuai dengan
          minatmu adalah{" "}
          <strong style={{ color: PRIMARY }}>{topProdi.nama}</strong>.
        </p>

        <h3 className="text-lg font-semibold text-slate-800">
          Hasil Rekomendasi Penjurusan
        </h3>

        <div className="space-y-3">
          {data.map((item, idx) => {
            const isTop = idx === 0;
            const percentageColor =
              item.persen >= 80
                ? "#0ea5a1"
                : item.persen >= 60
                ? PRIMARY
                : "#f97316";
            const badgeStyle = isTop
              ? { background: PRIMARY, color: "#fff" }
              : { background: "#eaf3fb", color: PRIMARY };

            return (
              <div
                key={item.kode}
                className="border rounded-lg p-3"
                style={{ borderColor: "#eff6fb", background: "#fff" }}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <div
                      style={badgeStyle}
                      className="w-9 h-9 rounded-md flex items-center justify-center font-semibold"
                    >
                      #{idx + 1}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-semibold text-slate-800 border-r-2">
                          {item.nama}
                        </h4>
                        {isTop && (
                          <span
                            style={{ background: "#eaf7ff", color: PRIMARY }}
                            className="text-base px-2 py-0.5 rounded"
                          >
                            Rekomendasi Utama
                          </span>
                        )}
                      </div>
                      <div
                        className="text-base font-semibold"
                        style={{ color: percentageColor }}
                      >
                        {item.persen}%{" "}
                        <span className="text-base text-slate-500 font-normal">
                          Kecocokan
                        </span>
                      </div>
                    </div>
                  </div>

                  <button
                    className="text-slate-400"
                    onClick={() =>
                      setExpandedProdi(
                        expandedProdi === item.kode ? null : item.kode
                      )
                    }
                  >
                    {expandedProdi === item.kode ? (
                      <ChevronUp size={18} />
                    ) : (
                      <ChevronDown size={18} />
                    )}
                  </button>
                </div>

                {expandedProdi === item.kode && (
                  <div
                    className="mt-3 border-t pt-3 text-base text-slate-700"
                    style={{ borderColor: "#eef6ff" }}
                  >
                    {item.summary.split("\n").map((line, i) => {
                      const trimmed = line.trim();
                      if (trimmed.startsWith("[") && trimmed.endsWith("]")) {
                        return (
                          <h5
                            key={i}
                            className="font-semibold"
                            style={{ color: PRIMARY, fontSize: 12 }}
                          >
                            {trimmed.replace(/^\[|\]$/g, "")}
                          </h5>
                        );
                      }
                      if (trimmed === "") return null;
                      return (
                        <p key={i} className="leading-relaxed">
                          {trimmed}
                        </p>
                      );
                    })}

                    {/* Tombol Lihat Kurikulum: biru + putih */}
                    <a
                      href={item.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-block mt-3 px-3 py-2 text-base rounded text-white font-medium"
                      style={{ background: PRIMARY }}
                    >
                      Lihat Kurikulum
                    </a>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Tombol ulangi tes – tetap full width */}
        <button
          onClick={() => window.location.reload()}
          className="w-full px-4 py-3 rounded-lg text-white font-semibold mt-4"
          style={{ background: PRIMARY }}
        >
          Ulangi Tes
        </button>
      </div>
    );
  };

  const AnswerButton = ({ optionKey, text, isSelected, onClick, disabled }) => {
    const [isHovered, setIsHovered] = useState(false);

    const bgColor = isSelected ? PRIMARY : isHovered ? PRIMARY : "#fff";
    const textColor = isSelected || isHovered ? "#fff" : "#1f2937";

    return (
      <button
        onClick={onClick}
        disabled={disabled}
        onMouseEnter={() => !isSelected && setIsHovered(true)}
        onMouseLeave={() => !isSelected && setIsHovered(false)}
        className="w-full text-left px-3 py-2 rounded-lg border flex items-center gap-3 text-base transition-colors duration-200"
        style={{
          background: bgColor,
          borderColor: isSelected ? PRIMARY : "#e7f0fb",
          color: textColor,
        }}
      >
        <div
          style={{
            background: isSelected || isHovered ? "#fff" : "#eaf3fb",
            color: PRIMARY,
          }}
          className="w-7 h-7 rounded-full flex items-center justify-center font-semibold"
        >
          {isSelected ? <Check size={14} /> : optionKey}
        </div>
        <div className="break-words">{text}</div>
      </button>
    );
  };

  const AnswerChoicesInChat = ({ children }) => (
    <div className="flex justify-end items-start gap-3 mb-3">
      <div className="max-w-md w-full flex flex-col items-end">
        <div
          className="rounded-2xl px-3 py-3 shadow-sm w-full"
          style={{ background: "#fff", border: "1px solid #e7f0fb" }}
        >
          {children}
          <p className="text-base text-slate-500 mt-2 text-center">
            Tidak ada yang salah dengan pilihan jawaban. Setiap jawaban
            merepresentasikan preferensi minatmu.
          </p>
        </div>
      </div>

      <div
        style={{ background: PRIMARY }}
        className="w-9 h-9 rounded-full flex items-center justify-center text-white flex-shrink-0"
      >
        <UserIcon className="w-4 h-4" />
      </div>
    </div>
  );

  return (
    <div style={{ background: BG }} className="min-h-screen">
      <div className="max-w-6xl mx-auto p-3 sm:p-6 min-h-screen flex flex-col">
        {/* Navbar */}
        <div
          className="rounded-xl p-3 sm:p-4 sticky top-0 z-20"
          style={{ background: PRIMARY }}
        >
          <h1 className="text-base sm:text-lg font-semibold text-white">
            Rekomendasi Prodi JTI Polindra
          </h1>
          <p className="text-base text-white/90 mt-1">
            Asisten rekomendasi program studi
          </p>
        </div>

        <div className="flex-1 flex flex-col lg:flex-row gap-4 mt-4 min-h-0">
          {/* CHAT COLUMN */}
          <div className="flex-1 flex flex-col min-h-0">
            <div
              className="flex-1 overflow-auto rounded-xl p-4 sm:p-6"
              style={{ background: "#fff", border: "1px solid #e7f0fb" }}
            >
              <div className="space-y-3">
                {messages.map((msg, idx) => (
                  <div key={idx}>
                    {msg.type === "bot" && !msg.isResults && (
                      <div className="flex items-start gap-3 mb-3">
                        <div
                          style={{ background: PRIMARY }}
                          className="w-9 h-9 rounded-full flex items-center justify-center text-white flex-shrink-0"
                        >
                          <RobotIcon className="w-4 h-4" />
                        </div>
                        <div
                          className="rounded-2xl px-3 py-2"
                          style={{
                            background: "#fff",
                            border: "1px solid #e7f0fb",
                          }}
                        >
                          <p className="text-slate-800 text-base whitespace-pre-line break-words">
                            {formatBoldText(msg.text)}
                          </p>
                        </div>
                      </div>
                    )}

                    {msg.type === "bot" && msg.isResults && (
                      <div className="flex items-start gap-3 mb-3">
                        <div
                          style={{ background: PRIMARY }}
                          className="w-9 h-9 rounded-full flex items-center justify-center text-white flex-shrink-0"
                        >
                          <RobotIcon className="w-4 h-4" />
                        </div>
                        <div className="w-full">
                          <ResultCard data={msg.data} />
                        </div>
                      </div>
                    )}

                    {msg.type === "user" && (
                      <div className="flex items-start gap-3 mb-3 justify-end">
                        <div
                          style={{ background: PRIMARY }}
                          className="text-white rounded-2xl px-3 py-2 max-w-xl"
                        >
                          <p className="text-base break-words">{msg.text}</p>
                        </div>
                        <div
                          className="w-9 h-9 rounded-full flex items-center justify-center text-white flex-shrink-0"
                          style={{ background: "#cfe6fb" }}
                        >
                          <UserIcon
                            className="w-4 h-4"
                            style={{ color: PRIMARY }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                {isTyping && <TypingIndicator />}

                {(stage === "welcome" || stage === "quiz") &&
                  showButtons &&
                  !isTyping && (
                    <AnswerChoicesInChat>
                      <div className="space-y-2">
                        {stage === "welcome" && (
                          <>
                            <AnswerButton
                              optionKey="A"
                              text="12 Soal (Cepat - 6 menit)"
                              isSelected={
                                selectedAnswer === "12 Soal (Cepat - 6 menit)"
                              }
                              onClick={() =>
                                handleNSoalSelect(
                                  12,
                                  "12 Soal (Cepat - 6 menit)"
                                )
                              }
                              disabled={!showButtons}
                            />
                            <AnswerButton
                              optionKey="B"
                              text="16 Soal (Standar - 8 menit)"
                              isSelected={
                                selectedAnswer === "16 Soal (Standar - 8 menit)"
                              }
                              onClick={() =>
                                handleNSoalSelect(
                                  16,
                                  "16 Soal (Standar - 8 menit)"
                                )
                              }
                              disabled={!showButtons}
                            />
                            <AnswerButton
                              optionKey="C"
                              text="20 Soal (Detail - 10 menit)"
                              isSelected={
                                selectedAnswer === "20 Soal (Detail - 10 menit)"
                              }
                              onClick={() =>
                                handleNSoalSelect(
                                  20,
                                  "20 Soal (Detail - 10 menit)"
                                )
                              }
                              disabled={!showButtons}
                            />
                          </>
                        )}
                        {stage === "quiz" && questions[currentQuestion] && (
                          <>
                            {Object.entries(
                              questions[currentQuestion].pilihan
                            ).map(([key, text]) => (
                              <AnswerButton
                                key={key}
                                optionKey={key}
                                text={text}
                                isSelected={
                                  selectedAnswer === `${key}. ${text}`
                                }
                                onClick={() => handleAnswerSelect(key, text)}
                                disabled={!showButtons}
                              />
                            ))}
                          </>
                        )}
                      </div>
                    </AnswerChoicesInChat>
                  )}

                {!showButtons && !isTyping && stage !== "result" && (
                  <div className="text-center text-base text-slate-400 py-3">
                    Tunggu sebentar...
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            </div>
          </div>

          {/* RIGHT SIDEBAR */}
          <div className="w-full lg:w-80 xl:w-96 flex flex-col min-h-0">
            <div
              className="rounded-xl p-4 shadow-sm sticky top-16"
              style={{ background: "#fff", border: "1px solid #e7f0fb" }}
            >
              <h2 className="text-base md:text-lg font-semibold text-slate-700">
                Status
              </h2>
              <p className="text-sm md:text-base text-slate-500 mt-2">
                {stage === "welcome" && (
                  <span>
                    Silakan pilih{" "}
                    <strong style={{ color: PRIMARY }}>jumlah soal</strong>{" "}
                    untuk memulai.
                  </span>
                )}
                {stage === "loading_questions" && (
                  <span>Memuat pertanyaan...</span>
                )}
                {stage === "quiz" && questions.length > 0 && (
                  <span>
                    <strong style={{ color: PRIMARY }}>{`Pertanyaan ${
                      currentQuestion + 1
                    }/${questions.length}`}</strong>
                  </span>
                )}
                {stage === "calculating" && (
                  <span>
                    <strong>Terima kasih.</strong> Sedang menganalisis
                    jawabanmu...
                  </span>
                )}
                {stage === "result" && (
                  <span>Hasil rekomendasi telah ditampilkan di chat.</span>
                )}
              </p>

              {stage === "quiz" && questions.length > 0 && (
                <div className="mt-3">
                  <div className="w-full bg-[#eef6ff] rounded-full h-2">
                    <div
                      className="h-2 rounded-full"
                      style={{
                        width: `${Math.round(
                          (currentQuestion / questions.length) * 100
                        )}%`,
                        background: PRIMARY,
                      }}
                    />
                  </div>
                  <div className="text-base text-slate-500 mt-2">
                    <strong style={{ color: PRIMARY }}>
                      {Math.round((currentQuestion / questions.length) * 100)}%
                    </strong>{" "}
                    selesai
                  </div>
                </div>
              )}
            </div>
            {/* Kolom "Informasi" dihapus sesuai permintaan */}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatApp;
