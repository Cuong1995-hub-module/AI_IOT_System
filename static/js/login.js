document.addEventListener("DOMContentLoaded", ()=>{

    const loginBtn=document.getElementById("login-btn");

    loginBtn.addEventListener("click",(e)=>{

        e.preventDefault();

        document.getElementById("loading-overlay").classList.add("show");

        const messages=[

            "[ OK ] Loading Dashboard",

            "[ OK ] Initializing AI Engine",

            "[ OK ] Starting Camera Service",

            "[ OK ] Connecting MQTT Broker",

            "[ OK ] Opening SQLite Database",

            "[ OK ] System Ready",

            "Launching Dashboard..."

        ];

        messages.forEach((msg,index)=>{

            setTimeout(()=>{

                const line=document.getElementById("line"+(index+1));

                if(msg.includes("[ OK ]")){

                    line.innerHTML=msg.replace(
                        "[ OK ]",
                        '<span class="ok">[ OK ]</span>'
                    );

                }else{

                    line.innerHTML=msg;

                }

                line.classList.add("show");

            },index*450);

        });

        setTimeout(()=>{

            document.body.classList.add("fade-out");

            setTimeout(()=>{

                loginBtn.closest("form").submit();

            },900);

        },4800);

    });

});