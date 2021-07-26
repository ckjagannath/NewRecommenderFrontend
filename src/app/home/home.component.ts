import { Component, OnInit, AfterViewInit, Input } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit,AfterViewInit {
  search;
  matchList;
  list;
  Qchart;
  Qarray = [];  //this contains tmdbids of movies in the queue
  tmdbid;
  recommendations;
  recom;
  background;
  constructor(private http:HttpClient) { }

  ngOnInit(): void {
  }

  ngAfterViewInit() :void{
    this.search = document.querySelector('#search');
    this.matchList = document.querySelector('#matchList');
    this.Qchart = document.querySelector("#queuechart");
    this.recom = document.querySelector("#recChart");
    this.background = document.querySelector(".background");
    this.search.addEventListener('keyup',(e)=>{
      if(e.key === 'Enter'){
        this.searchMovie(this.search.value);
      } 
    })
    document.addEventListener("click",(e)=>{
      if((e.target as Element).id == "tmdbid"){
        var id = (e.target as Element).innerHTML;
        if (!(this.Qarray.includes(id))){
          this.Qarray.push(id);
          this.getId(id);
        }
        else{
          alert("Movie already in queue");
        }  
      }
    })
    document.querySelector("#steps").addEventListener("click", ()=>{
      alert(
        "Steps to Play\n" +
        "-> Type few letters in the search and press Enter.\n" +
        "-> To prevent search from suggestions clear the search and press Enter.\n" +
        "-> Choose from suggestions by clicking on blue Tmdbid to add to queue.\n" +
        "-> Add as many as you want, so that upto 5 movies are recommended for each movie in queue.\n" +
        "-> Select any genre from Top movies dropup to get popular movies.\n" +
        "-> Click on any movie image for information."
        );
    })
    document.addEventListener("click", (e)=>{
      if((e.target as HTMLElement).tagName === "IMG"){
          var id = (e.target as HTMLElement)['alt']
          window.open(`https://www.themoviedb.org/movie/${id}`);
      }
    })
    }
    outputHtml(list){
      var list = list;
      if (list.length > 0){
        const html = list.map(item => `
          <div class="container text-white bg-secondary" style="height:auto; width: 260px; border-radius:10px; border: white 1px solid;">
            <div class="row pt-1 pb-1">
              <div class="col-md-10">
                <h6 style="font-size: 13px;font-weight:900px;">${item[0]}</h6> 
                <div style="line-height:11px;">
                  <span style="font-size: 12px; font-weight:700px">TmdbId: </span>
                  <span id="tmdbid" style="color:cyan; font-weight:900px; font-size: 14px;">${item[1]}</span>
                </div>
              </div>
              <div class="col-md-2" id="image" style="margin-top:auto; margin-bottom:auto;">
                <img onerror="this.style.display='none'" src="../../../assets/images_100k/${item[1]}.0.jpg" alt="${item[1]}" width="26px" height="39px" style="border: cyan 1px solid; margin-left:-15px">
              </div>
            </div>   
          </div>
        `).join('');

        this.matchList.innerHTML = html;
      }
      else{
        this.matchList.innerHTML = '';
      }
    }
    searchMovie(s){
      var searchstring = s
      this.http.post(
        environment.SERVER_URL +'/search',
        {searchstring},
        {}
      ).subscribe((res: any)=>{
        this.list = res;
        this.outputHtml(this.list);
      })  
    }
    getId(value){
      this.tmdbid = value;
      var img = document.createElement('img');
      img.src =  `../../../assets/images_100k/${this.tmdbid}.0.jpg`;
      img.alt = `${value}`;
      img.width = 100;
      img.height = 150;
      img.onerror = (()=>{img.style.display = 'none'})
      img.style.marginLeft = "5px";
      img.style.border = "cyan 2px solid";
      this.Qchart.prepend(img);
      this.getRecommendation(value);
    }
    getRecommendation(value){
      this.http.post(
        environment.SERVER_URL +'/recommend',
        {value},
        {responseType:'text'}
      ).subscribe((result: any)=>{
        result = JSON.parse(result);
        this.recommendations = result;
        this.recChart(this.recommendations);
      })  
    }
    recChart(array){
      var listofmovies = array;
      if (listofmovies.length > 0){
        var img = listofmovies.map(item => `
            <img onerror="this.style.display='none'" src="../../../assets/images_100k/${item}.0.jpg" alt="${item}" width="100px" height="150px" style="border: cyan 2px solid;">
        `).join('');
        if (this.recom.children.length > 0){
          img += document.querySelector("#recommended").innerHTML;
          document.querySelector("#recommended").innerHTML = img;
          return;
        }
          var html = `
        <div class="mt-4">
          <h5 style="color:white; margin-left:20px;">Recommended Movies</h5>
          <div id="recommended" class="container mb-2 pb-1 pt-2" style="overflow:auto; white-space:nowrap;">` + img + 
          `</div>
        </div>`
        this.recom.innerHTML = html;
        } 
    }
}

