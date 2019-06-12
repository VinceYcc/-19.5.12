//验证码
function yanZ(length){
    //定义数据源
    var num = ["q","w","e","r","t","y","u","i","o","p","l","k","j","h",
    "g","f","d","s","a","z","x","c","v","b","n","m","Q","W","E","R","Y","U","I","O","P","L","K","J"
    ,"H","G","F","D","S","A","Z","X","C","V","B","N","M","0","1","2","3","4","5","6","7","8","9"]

     // 定义验证码,随机取元素
     var code="";
     var checkCode = document.getElementById("checkCode");
     for(var i=0;i<length;i++){
        //随机下标
        var index = parseInt(Math.random()*num.length);
        code += num[index];
     }
        //为验证码区域添加样式名
        checkCode.className = "code";
        //将生成验证码赋值到显示区
        checkCode.value = code;

     }

    function validateCode()
        {
        //获取显示区生成的验证码
        var checkCode = document.getElementById("checkCode").value;
        //获取输入的验证码
        var inputCode = document.getElementById("inputCode").value;
        console.log(checkCode)
        console.log(inputCode)
        if (inputCode.length <= 0)
        {
            alert("请输入验证码！");
            return

        }
        else if (checkCode.toUpperCase() != inputCode.toUpperCase())
        {
            alert("验证码输入有误！");
            return

        }
//        else
//        {
//            alert("验证码正确！");
//        }
    }















