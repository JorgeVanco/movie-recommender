const search = (e, setMovies) => {
    e.preventDefault();
    const query = document.getElementById('search').value;
    const url = `http://localhost:5000/search?title=${query}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Display the search results
            setMovies(data);
    });
}

const getSimilarMovies = (movie, setMovies) => {
    const url = `http://localhost:5000/similar?idx=${movie.idx}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            setMovies(data);
            // Display the similar movies
    });

}

const Movie = ({movie, setMovies}) => {
    
    return (
        <div className="card">
            <img src={movie.img} onClick = {() => {getSimilarMovies(movie, setMovies)}}></img>
            <div className="cardInfo">
                <a style ={{color:"yellow"}} href = {movie.url}>{movie.title}</a>
                <p style ={{color:"greenyellow"}}>{movie.year}</p>
            </div>
        </div>
    )
}

const MovieList = ({movies, setMovies}) => {
    return (
        <div id = "movieList" className="flex">
            {movies.map((d, idx) => {
                return <Movie key = {idx}  movie = {d} setMovies ={setMovies}/>
            })}
        </div>
    )
}

const App = () => {
    const [movies, setMovies] = React.useState([]);
    React.useEffect(() => {

        fetch('http://localhost:5000/')
            .then(response => response.json())
            .then(data => {
                // Display the movies
                setMovies(data);
            });
    }, [])


    return (
        <div>
            <form onSubmit={(e) => {search(e, setMovies)}}>
                <input type="text" id="search" placeholder="Search for movies"/>
            </form>
            <MovieList movies = {movies} setMovies = {setMovies}/>
        </div>
    )
    
}


ReactDOM.render(<App/>, document.getElementById('wrap'));