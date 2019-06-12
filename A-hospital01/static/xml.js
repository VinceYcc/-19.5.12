function createXhr (){
    if(window.XMLHttpRequest){
    alert;
    return new XMLHttpRequest();
    }else{
    return new ActiveXObject("Microsoft.XMLHTTP");
    }

}
function check_name(){
    var ret = false;
    $.ajax({
        url:"/reg",
        type:"get",
        data:"id_card="+$("#d1").val(),
        async:true,
        dataType:"json",
        success:function(data){
            console.log(data)
        }
    });
  };