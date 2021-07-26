import { Component, OnInit, AfterViewInit, Input, Output, EventEmitter } from '@angular/core';
import { environment } from 'src/environments/environment';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-recommend',
  templateUrl: './recommend.component.html',
  styleUrls: ['./recommend.component.css']
})
export class RecommendComponent implements OnInit, AfterViewInit {
  ids;
  chartEle;
  category;
  height;
  genres = ['Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 
            'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'];
  genresfirst = this.genres.slice(0,9);
  genressecond = this.genres.slice(9,);
  constructor(private http:HttpClient) { 
   }

  ngOnInit(): void {
  }
  ngAfterViewInit(): void{
    document.querySelector(".dropdown-menu").addEventListener("click", (e)=>{
      if(e.target !== e.currentTarget){
        var genre = (e.target as Element).innerHTML;
        this.category = genre;
        this.getMoviesByGenre(genre);
      }
    })
    this.chartEle = document.querySelector("#topchart");
  }
  outputhtml(ids_list){
    var ids = ids_list;
    var html = ids.map(item => `
            <img onerror="this.style.display='none'" src="../../../assets/top_movieimages/${item}.0.jpg" alt="${item}" width="100px" height="150px" style="border: cyan 2px solid;">
        `).join('');
        html = `
        <div class="mt-4">
          <h5 style="color:white; margin-left:20px;">Top Movies: ${this.category}</h5>
          <div class="container mb-2 pb-1 pt-2" style="overflow:auto; white-space:nowrap;">` + html + 
          `</div>
        </div>`
        this.chartEle.innerHTML = html;
  }
  getMoviesByGenre(genre){
    var genre = genre;
    this.http.post(
      environment.SERVER_URL +'/genre',
      {genre},
      {}
    ).subscribe((res: any)=>{
      this.ids = res;
      this.outputhtml(this.ids);
  })
  }
}
