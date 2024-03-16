import React from 'react';

const Pet = ({ name, likes, media }) => {
  return (
    <div className="pet-grid">
      <div className="pet-name">
        <h2>{name}</h2>
      </div>
      <div className="pet-likes">
        <h3>Likes:</h3>
        <p>{likes}</p>
      </div>
      <div className="pet-media-title">
        <h3>Photo Gallery</h3>
      </div>
      <div className="pet-media">
        {media.map((item, index) => (
          <div className="pet-media-piece" key={index}>
            {item.type === 'image' ? (
              <img src={item.url} alt={item.alt} />
            ) : (
              <video controls>
                <source src={item.url} />
                Your browser does not support the video tag.
              </video>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Pet;
