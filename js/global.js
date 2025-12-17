const modal = document.getElementById("modal");
const closeBtn = document.querySelector(".close");

if (closeBtn && modal) {
 closeBtn.onclick = () => {
   modal.style.display = "none";
 };

 window.onclick = (e) => {
   if (e.target === modal) {
     modal.style.display = "none";
   }
 };
}
